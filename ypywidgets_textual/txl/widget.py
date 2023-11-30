import asyncio
from functools import lru_cache
from typing import Callable

import pyte
from rich.color import Color, parse_rgb_hex
from rich.console import RenderableType
from rich.segment import Segment
from rich.style import Style
from textual import events
from textual.widget import Widget as TextualWidget
from wcwidth import wcwidth as _wcwidth

from ..widget import WidgetModel


wcwidth: Callable[[str], int] = lru_cache(maxsize=4096)(_wcwidth)


CTRL_KEYS = {
    "left": "\u001b[D",
    "right": "\u001b[C",
    "up": "\u001b[A",
    "down": "\u001b[B",
}


class PyteDisplay:
    def __init__(self, screen):
        self._screen = screen
        self._cache = {}

    def __rich_console__(self, console, options):
        if self._screen is None:
            return

        dirty_lines = {y: self._render_line(self._screen.buffer[y]) for y in self._screen.dirty}
        self._screen.dirty.clear()
        init = not self._cache
        for y in range(self._screen.lines):
            dirty_line = y in dirty_lines
            if init or dirty_line:
                self._cache[y] = cache = []
                if dirty_line:
                    line = dirty_lines[y]
                else:
                    line = self._render_line(self._screen.buffer[y])
                for char in line:
                    color = None if char.fg == "default" else Color.from_triplet(parse_rgb_hex(char.fg))
                    bgcolor = None if char.bg == "default" else Color.from_triplet(parse_rgb_hex(char.bg))
                    cache.append(
                        Segment(
                            char.data,
                            Style(
                                color=color,
                                bgcolor=bgcolor,
                                bold=char.bold,
                                italic=char.italics,
                                underline=char.underscore,
                                blink=char.blink,
                                strike=char.strikethrough,
                                reverse=char.reverse,
                            )
                        )
                    )
                cache.append(Segment("\n"))

        for y in range(self._screen.lines):
            for segment in self._cache[y]:
                yield segment

    def _render_line(self, line):
        is_wide_char = False
        for x in range(self._screen.columns):
            if is_wide_char:
                is_wide_char = False
                continue
            char = line[x].data
            assert sum(map(wcwidth, char[1:])) == 0
            is_wide_char = wcwidth(char[0]) == 2
            yield line[x]


class Terminal(TextualWidget, can_focus=True):
    DEFAULT_CSS = """
    Terminal {
        height: 1fr;
    }
    """

    def __init__(self, send_queue, recv_queue):
        super().__init__()
        self._send_queue = send_queue
        self._recv_queue = recv_queue
        self._display = PyteDisplay(None)
        self._tasks = [asyncio.create_task(self._recv())]
        self._ready_event = asyncio.Event()

    def render(self) -> RenderableType:
        return self._display

    def on_resize(self, event: events.Resize):
        self.do_resize(event.size.width, event.size.height)

    def do_resize(self, cols: int, rows: int):
        if self.ymodel._cols != cols:
            self.ymodel._cols = cols
        if self.ymodel._rows != rows:
            self.ymodel._rows = rows
        self.ymodel._ready = True
        self._ready_event.set()
        self._screen = pyte.Screen(cols, rows)
        self._stream = pyte.Stream(self._screen)

    async def on_event(self, event: events.Event) -> None:
        await super().on_event(event)
        if isinstance(event, events.Key):
            char = CTRL_KEYS.get(event.key) or event.character
            await self._send_queue.put("")
            await self._send_queue.put(char)
            event.stop()
            return
        if isinstance(event, events.MouseMove):
            char = f"\x1b[<35;{event.x};{event.y}M"
            await self._send_queue.put("")
            await self._send_queue.put(char)
            event.stop()
            return
        if isinstance(event, events.MouseDown):
            char = f"\x1b[<0;{event.x};{event.y}M"
            await self._send_queue.put("")
            await self._send_queue.put(char)
            event.stop()
            return
        if isinstance(event, events.MouseUp):
            char = f"\x1b[<0;{event.x};{event.y}m"
            await self._send_queue.put("")
            await self._send_queue.put(char)
            event.stop()
            return

    async def _recv(self):
        while True:
            data = await self._recv_queue.get()
            if not data:
                continue
            self._stream.feed(data)
            self._display = PyteDisplay(self._screen)
            self.refresh()


class Widget(Terminal):

    def __init__(self, model: WidgetModel) -> None:
        self.ymodel = model
        self._data_from_app_queue = asyncio.Queue()
        self._data_to_app_queue = asyncio.Queue()
        super().__init__(self._data_to_app_queue, self._data_from_app_queue)
        model.watch__data_from_app = self._to_terminal
        self._tasks = [asyncio.create_task(self._from_terminal())]

    def _to_terminal(self, data: str) -> None:
        self._data_from_app_queue.put_nowait(data)

    async def _from_terminal(self):
        while True:
            data = await self._data_to_app_queue.get()
            self.ymodel._data_to_app = data

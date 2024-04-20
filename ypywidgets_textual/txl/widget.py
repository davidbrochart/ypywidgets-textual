import asyncio
from functools import lru_cache
from typing import Callable

import pyte
from rich.color import Color, parse_rgb_hex
from rich.console import RenderableType
from rich.segment import Segment
from rich.style import Style
from textual import events
from textual.geometry import Region
from textual.strip import Strip
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
        self._dirty = set()

    def get_line(self, y: int) -> Strip:
        self._dirty.update(self._screen.dirty)
        self._screen.dirty.clear()
        if y in self._dirty or y not in self._cache:
            line = self._screen.buffer[y]
            is_wide_char = False
            segments = []
            for x in range(self._screen.columns):
                if is_wide_char:
                    is_wide_char = False
                    continue
                char = line[x].data
                assert sum(map(wcwidth, char[1:])) == 0
                is_wide_char = wcwidth(char[0]) == 2
                char = line[x]
                color = None if char.fg == "default" else Color.from_triplet(parse_rgb_hex(char.fg))
                bgcolor = None if char.bg == "default" else Color.from_triplet(parse_rgb_hex(char.bg))
                segments.append(
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
            self._cache[y] = Strip(segments)
            if y in self._dirty:
                self._dirty.remove(y)
        return self._cache[y]


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
        self._screen = pyte.Screen(0, 0)
        self._stream = pyte.Stream(self._screen)
        self._display = PyteDisplay(self._screen)
        self._tasks = [asyncio.create_task(self._recv())]

    def render_line(self, y: int) -> Strip:
        return self._display.get_line(y)

    def on_resize(self, event: events.Resize):
        self.do_resize(event.size.width, event.size.height)

    def do_resize(self, cols: int, rows: int):
        if self.ymodel._cols != cols:
            self.ymodel._cols = cols
        if self.ymodel._rows != rows:
            self.ymodel._rows = rows
        self.ymodel._ready = False
        self.ymodel._ready = True
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
            for y in self._screen.dirty:
                region = Region(0, y, self._screen.columns, 1)
                self.refresh(region)


class Widget(Terminal):

    def __init__(self, model: WidgetModel) -> None:
        self.ymodel = model
        self._data_from_app_queue = asyncio.Queue()
        self._data_to_app_queue = asyncio.Queue()
        super().__init__(self._data_to_app_queue, self._data_from_app_queue)

        @WidgetModel._data_from_app.watch
        def _watch__data_from_app(obj, old: str, new: str):
            if obj != model:
                return

            self._to_terminal(new)

        self._tasks = [asyncio.create_task(self._from_terminal())]

    def _to_terminal(self, data: str) -> None:
        self._data_from_app_queue.put_nowait(data)

    async def _from_terminal(self):
        while True:
            data = await self._data_to_app_queue.get()
            self.ymodel._data_to_app = data

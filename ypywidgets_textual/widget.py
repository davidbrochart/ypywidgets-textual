from __future__ import annotations

import asyncio
import json
from typing import Type

from textual import events
from textual.app import App
from textual.geometry import Size
from ypywidgets import Reactive, Widget as _Widget
from ypywidgets.comm import CommWidget

from ._driver import Driver


class WidgetModel(_Widget):
    _data_from_app = Reactive[str]("")
    _data_to_app = Reactive[str]("")
    _cols = Reactive[int](0)
    _rows = Reactive[int](0)
    _ready = Reactive[bool](False)

    def __init__(
        self,
        ydoc=None,
    ) -> None:
        super().__init__(ydoc)


class Widget(CommWidget, WidgetModel):

    def __init__(self, app_class: Type[App]) -> None:
        CommWidget.__init__(self)
        WidgetModel.__init__(self)
        self._app = app_class(driver_class=Driver)
        self._cols = 0
        self._rows = 0
        self._data_from_app_queue = asyncio.Queue()
        self._data_to_app_queue = asyncio.Queue()
        self._tasks = [
            asyncio.create_task(self._run()),
            asyncio.create_task(self._send_data()),
            asyncio.create_task(self._recv_data()),
        ]

        @WidgetModel._ready.watch
        def _watch__ready(obj, old: bool, value: bool):
            if obj != self:
                return

            if value:
                size = Size(int(obj._cols), int(obj._rows))
                loop = asyncio.get_running_loop()
                event = events.Resize(size, size)
                asyncio.run_coroutine_threadsafe(
                    self._app._post_message(event),
                    loop=loop,
                )

        @WidgetModel._data_to_app.watch
        def _watch__data_to_app(obj, old:str, data: str):
            if obj != self:
                return

            if data:
                obj._data_to_app_queue.put_nowait(data)

    async def _send_data(self):
        while True:
            data = await self._data_from_app_queue.get()
            self._data_from_app = ""
            self._data_from_app = data.decode()

    async def _recv_data(self):
        while True:
            data = await self._data_to_app_queue.get()
            if not data:
                continue
            data = data.encode()
            packet_type = b"D"
            packet = b"%s%s%s" % (packet_type, len(data).to_bytes(4, "big"), data)
            self._app._driver._stdin_queue.put_nowait(packet)

    async def _run(self):
        self._tasks.append(asyncio.create_task(self._app.run_async()))
        while True:
            if self._app._driver is not None:
                break
            await asyncio.sleep(0)

        for _ in range(10):
            line = []
            while True:
                data = await self._app._driver._stdout_queue.get()
                line.append(data)
                if data[-1] == 10:  # "\n"
                    break
            line = b"".join(line)
            if not line:
                break
            if line == b"__GANGLION__\n":
                ready = True
                break
        if ready:
            META = 77  # b"M"
            DATA = 68  # b"D"
            while True:
                data = await self._app._driver._stdout_queue.get()
                type_bytes = data[0]
                size_bytes = data[1:5]
                size = int.from_bytes(size_bytes, "big")
                data = data[5:5 + size]
                if type_bytes == DATA:
                    self._data_from_app_queue.put_nowait(data)
                elif type_bytes == META:
                    meta_data = json.loads(data)
                    #if meta_data.get("type") == "exit":
                    #    await self.send_meta({"type": "exit"})
                    #else:
                    #    await on_meta(json.loads(data))

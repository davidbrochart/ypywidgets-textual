from typing import Any, Callable

from ypywidgets import Widget as _Widget


class Widget(_Widget):
    def on_change(self, name: str, callback: Callable[[Any], None]) -> None:
        callbacks = getattr(self, f"_{name}_callbacks", None)
        if callbacks is not None:
            callbacks.append(callback)
            return

        callbacks = [callback]
        setattr(self, f"_{name}_callbacks", callbacks)
        def on_change(self, callback):
            callbacks.append(callback)
        setattr(self, f"_on_{name}_change", on_change)
        def watch(self, value):
            for callback in callbacks:
                callback(value)
        setattr(self, f"watch_{name}", watch)

from __future__ import annotations

from ypywidgets import Reactive, Widget
from ypywidgets.comm import CommWidget


class PlotextModel(Widget):

    _clear_data = Reactive[bool](False)
    _args = Reactive[list]([])
    _scatter = Reactive[bool](False)
    _plot = Reactive[bool](False)
    _title = Reactive[str]("")

    def __init__(self, ydoc=None) -> None:
        super().__init__(ydoc)

    def clear_data(self) -> None:
        self._clear_data = False
        self._clear_data = True

    def scatter(self, *args) -> None:
        self._args = list(args)
        self._scatter = False
        self._scatter = True

    def plot(self, *args) -> None:
        self._args = list(args)
        self._plot = False
        self._plot = True

    def title(self, value: str) -> None:
        self._title = value


class Plotext(CommWidget, PlotextModel):

    def __init__(self) -> None:
        CommWidget.__init__(self)
        PlotextModel.__init__(self)

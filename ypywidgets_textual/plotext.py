from ypywidgets import Widget, reactive


class Plotext(Widget):

    _clear_data = reactive(False)
    _args = reactive([])
    _scatter = reactive(False)
    _plot = reactive(False)
    _title = reactive("")

    def __init__(self, primary: bool = True) -> None:
        super().__init__(primary=primary)

    def clear_data(self) -> None:
        self._clear_data = not self._clear_data

    def scatter(self, *args) -> None:
        self._args = list(args)
        self._scatter = not self._scatter

    def plot(self, *args) -> None:
        self._args = list(args)
        self._plot = not self._plot

    def title(self, value: str) -> None:
        self._title = value

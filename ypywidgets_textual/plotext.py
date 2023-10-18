from ypywidgets import Widget, reactive


class Plotext(Widget):

    _clear_data = reactive(False)
    _args = reactive([])
    _scatter = reactive(False)
    _plot = reactive(False)
    _title = reactive("")

    def __init__(self, primary: bool = True) -> None:
        super().__init__(primary=primary)
        self._clear_data_change_callbacks = []
        self._scatter_change_callbacks = []
        self._plot_change_callbacks = []
        self._title_change_callbacks = []

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

    def _on__clear_data_change(self, cb):
        self._clear_data_change_callbacks.append(cb)

    def _on__scatter_change(self, cb):
        self._scatter_change_callbacks.append(cb)

    def _on__plot_change(self, cb):
        self._plot_change_callbacks.append(cb)

    def _on__title_change(self, cb):
        self._title_change_callbacks.append(cb)

    def watch__clear_data(self, value: bool) -> None:
        for cb in self._clear_data_change_callbacks:
            cb(value)

    def watch__scatter(self, value) -> None:
        for cb in self._scatter_change_callbacks:
            cb(value)

    def watch__plot(self, value) -> None:
        for cb in self._plot_change_callbacks:
            cb(value)

    def watch__title(self, value: str) -> None:
        for cb in self._title_change_callbacks:
            cb(value)

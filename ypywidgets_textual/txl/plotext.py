from textual_plotext import PlotextPlot

from ..plotext import PlotextModel


class Plotext(PlotextPlot):

    def __init__(self, model: PlotextModel) -> None:
        super().__init__()
        self.ymodel = model

        @PlotextModel._clear_data.watch
        def _watch__clear_data(obj, old, new):
            if obj != model:
                return

            self.clear_data()

        @PlotextModel._scatter.watch
        def _watch__scatter(obj, old, new):
            if obj != model:
                return

            self.scatter()

        @PlotextModel._plot.watch
        def _watch__plot(obj, old, new):
            if obj != model:
                return

            self.plot()

        @PlotextModel._title.watch
        def _watch__title(obj, old: str, new: str):
            if obj != model:
                return

            self.title(new)

        self.clear_data()
        self.scatter()
        self.plot()
        self.title(model._title)

    def clear_data(self) -> None:
        if self.ymodel._clear_data:
            self.plt.clear_data()
            self.refresh()

    def title(self, value: str) -> None:
        self.plt.title(value)
        self.refresh()

    def scatter(self) -> None:
        if self.ymodel._scatter:
            self.plt.clear_data()
            self.plt.scatter(*self.ymodel._args)
            self.refresh()

    def plot(self) -> None:
        if self.ymodel._plot:
            self.plt.clear_data()
            self.plt.plot(*self.ymodel._args)
            self.refresh()

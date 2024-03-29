from textual_plotext import PlotextPlot

from ..plotext import PlotextModel


class Plotext(PlotextPlot):

    def __init__(self, model: PlotextModel) -> None:
        super().__init__()
        self.ymodel = model
        model.watch__clear_data = self.clear_data
        model.watch__scatter = self.scatter
        model.watch__plot = self.plot
        model.watch__title = self.title
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

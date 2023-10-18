from textual_plotext import PlotextPlot

from ..plotext import Plotext as PlotextModel


class Plotext(PlotextPlot):

    def __init__(self, model: PlotextModel) -> None:
        super().__init__()
        self.ymodel = model
        model.on_change("_clear_data", self.clear_data)
        model.on_change("_scatter", self.scatter)
        model.on_change("_plot", self.plot)
        model.on_change("_title", self.title)

    def clear_data(self, value: bool) -> None:
        self.plt.clear_data()
        self.refresh()

    def title(self, value: str) -> None:
        self.plt.title(value)
        self.refresh()

    def scatter(self, value: bool) -> None:
        self.plt.clear_data()
        self.plt.scatter(*self.ymodel._args)
        self.refresh()

    def plot(self, value: bool) -> None:
        self.plt.clear_data()
        self.plt.plot(*self.ymodel._args)
        self.refresh()

from textual_plotext import PlotextPlot

from ..plotext import Plotext as PlotextModel


class Plotext(PlotextPlot):

    def __init__(self, model: PlotextModel) -> None:
        super().__init__()
        self.ymodel = model
        model._on__clear_data_change(self.clear_data)
        model._on__scatter_change(self.scatter)
        model._on__plot_change(self.plot)
        model._on__title_change(self.title)

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

from textual.widgets import Switch as TextualSwitch

from ..switch import Switch as SwitchModel


class Switch(TextualSwitch):

    def __init__(self, model: SwitchModel) -> None:
        super().__init__()
        self.ymodel = model
        model._on_value_change(self._update_value)

    def watch_value(self, value: bool) -> None:
        super().watch_value(value)
        if value != self.ymodel.value:
            self.ymodel.value = value

    def _update_value(self, value: bool) -> None:
        if value != self.value:
            self.value = value

from textual.widgets import Button as TextualButton

from ..button import ButtonModel


class Button(TextualButton):

    def __init__(self, model: ButtonModel) -> None:
        super().__init__()
        self.ymodel = model
        model.watch__press = self.action_press
        model.watch_label = self._set_label
        model.watch_variant = self._set_variant
        model.watch_disabled = self._set_disabled
        self._set_label(model.label)
        self._set_variant(model.variant)
        self._set_disabled(model.disabled)

    def on_button_pressed(self, event) -> None:
        self.ymodel._pressed = not self.ymodel._pressed

    def _set_label(self, value: str) -> None:
        if value != self.label:
            self.label = value

    def _set_variant(self, value: str) -> None:
        if value != self.variant:
            self.variant = value

    def _set_disabled(self, value: str) -> None:
        if value != self.disabled:
            self.disabled = value

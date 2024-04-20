from textual.widgets import Button as TextualButton

from ..button import ButtonModel


class Button(TextualButton):

    def __init__(self, model: ButtonModel) -> None:
        super().__init__()
        self.ymodel = model

        @ButtonModel._press.watch
        def _watch__press(obj, old, new):
            if obj != model:
                return

            self.action_press()

        @ButtonModel.label.watch
        def _watch_label(obj, old: str, new: str):
            if obj != model:
                return

            self._set_label(new)

        @ButtonModel.variant.watch
        def _watch_variant(obj, old: str, new: str):
            if obj != model:
                return

            self._set_variant(new)

        @ButtonModel.disabled.watch
        def _watch_disabled(obj, old: bool, new: bool):
            if obj != model:
                return

            self._set_disabled(new)

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

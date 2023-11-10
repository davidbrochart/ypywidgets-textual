from __future__ import annotations

from typing import Callable

from ypywidgets import Widget, reactive
from ypywidgets.comm import CommWidget


class ButtonModel(Widget):

    label = reactive("")
    variant = reactive("default")
    disabled = reactive(False)
    _press = reactive(False)
    _pressed = reactive(False)

    def __init__(
        self,
        label: str = "",
        variant: str = "default",
        disabled: bool = False,
        on_button_pressed: Callable[[], None] | None = None,
        ydoc=None,
    ) -> None:
        super().__init__(ydoc)
        self.label = label
        self.variant = variant
        self.disabled = disabled
        if on_button_pressed is None:
            def no_op():
                pass
            self._on_button_pressed = no_op
        else:
            self._on_button_pressed = on_button_pressed

    @property
    def on_button_pressed(self) -> Callable[[], None]:
        return self._on_button_pressed

    @on_button_pressed.setter
    def on_button_pressed(self, value: Callable[[], None]) -> None:
        self._on_button_pressed = value

    def action_press(self):
        self._press = not self._press

    def watch__pressed(self):
        self._on_button_pressed()


class Button(CommWidget, ButtonModel):

    def __init__(
        self,
        label: str = "",
        variant: str = "default",
        disabled: bool = False,
        on_button_pressed: Callable[[], None] | None = None,
    ):
        CommWidget.__init__(self)
        ButtonModel.__init__(self, label, variant, disabled, on_button_pressed)

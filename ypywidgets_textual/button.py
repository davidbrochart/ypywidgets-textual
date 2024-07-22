from __future__ import annotations

from typing import Callable

from ypywidgets import Reactive, Widget
from ypywidgets.comm import CommWidget


class ButtonModel(Widget):

    label = Reactive[str]("")
    variant = Reactive[str]("default")
    disabled = Reactive[bool](False)
    _press = Reactive[bool](False)
    _pressed = Reactive[bool](False)

    def __init__(
        self,
        label: str | None = None,
        variant: str | None = None,
        disabled: bool | None = None,
        on_button_pressed: Callable[[], None] | None = None,
        ydoc=None,
    ) -> None:
        super().__init__(ydoc)
        if label is not None:
            self.label = label
        if variant is not None:
            self.variant = variant
        if disabled is not None:
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

    @_pressed.watch
    def _watch__pressed(self, old: bool, new: bool):
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

from __future__ import annotations

from ypywidgets import Widget, reactive
from ypywidgets.comm import CommWidget


class SwitchModel(Widget):
    value = reactive(False)

    def __init__(
        self,
        value: bool | None = None,
        ydoc=None,
    ) -> None:
        super().__init__(ydoc)
        if value is not None:
            self.value = value

    def toggle(self):
        self.value = not self.value


class Switch(CommWidget, SwitchModel):

    def __init__(self, value: bool = False) -> None:
        CommWidget.__init__(self)
        SwitchModel.__init__(self, value)

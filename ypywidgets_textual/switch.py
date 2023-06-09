from ypywidgets import Widget, reactive


class Switch(Widget):

    value = reactive(False)

    def __init__(self, value: bool = False, primary: bool = True) -> None:
        super().__init__(primary=primary)
        self.value_change_callbacks = []
        self.value = value

    def toggle(self):
        self.value = not self.value

    def on_value_change(self, cb):
        self.value_change_callbacks.append(cb)

    def watch_value(self, value: bool) -> None:
        for cb in self.value_change_callbacks:
            cb(value)

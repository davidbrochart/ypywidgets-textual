from ypywidgets import Widget, reactive


class Switch(Widget):

    value = reactive(False)

    def __init__(self, value: bool = False, primary: bool = True) -> None:
        super().__init__(primary=primary)
        self.value = value

    def toggle(self):
        self.value = not self.value

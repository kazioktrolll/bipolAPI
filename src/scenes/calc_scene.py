from .scene import Scene
from ..frontend import CalcDisplay


class CalcScene(Scene):
    def __init__(self, app):
        self.display = None
        super().__init__(app)

    def build(self) -> None:
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.display = CalcDisplay(self)
        self.display.grid(row=0, column=0)
        self.display.build()

from functools import cached_property
from .scene import Scene
from ..frontend import CalcDisplay


class CalcScene(Scene):
    @cached_property
    def display(self):
        return CalcDisplay(self)

    def build(self) -> None:
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.display.grid(row=0, column=0, sticky='news')

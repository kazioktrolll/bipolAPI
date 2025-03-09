from ..scenes import Scene
from ..frontend import CalcDisplay


class CalcScene(Scene):
    def __init__(self, app):
        self.display = None
        super().__init__(app)

    def build(self) -> None:
        self.display = CalcDisplay(self)

from src.backend.geo_design import Geometry


class App:
    def __init__(self, geometry: Geometry):
        self.geometry = geometry
        from customtkinter import CTk
        self.root = CTk()
        from ..scenes.calc_scene import CalcScene
        CalcScene(self, self).pack()

    def run(self) -> None:
        """Runs the app."""
        # self.root.after(0, self.root.state, 'zoomed')   # noqa
        self.root.mainloop()

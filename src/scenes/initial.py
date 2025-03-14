from .scene import Scene
from .geo_design import GeoDesignScene
from .calc_scene import CalcScene
from customtkinter import CTkButton


class InitialScene(Scene):
    def build(self) -> None:
        self.rowconfigure(0, weight=0, minsize=10)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0, minsize=10)
        self.columnconfigure(0, weight=0, minsize=10)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0, minsize=10)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=0, minsize=10)

        CTkButton(self, text="Geometry\nDesign", command=lambda: self.app.set_scene(GeoDesignScene(self.app))
                  ).grid(row=1, column=1, sticky="nsew")
        CTkButton(self, text="Calculations", command=lambda: self.app.set_scene(CalcScene(self.app))
                  ).grid(row=1, column=3, sticky="nsew")
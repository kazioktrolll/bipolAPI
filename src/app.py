from pathlib import Path
from typing import Callable, Any, ClassVar


class App:
    geo_path: Path
    mass_path: Path
    run_path: Path
    def __init__(self):
        from customtkinter import CTk
        from .scenes import Scene
        from .backend.geo_design import Geometry
        self.root = CTk()
        self.scene = Scene(self)
        self.geometry: Geometry = Geometry('Plane', 8, 1, 8, ref_pos=(.5, 0, 0))    # Placeholder
        self.root.bind('<Configure>', self.update)
        self.build()

    def build(self) -> None:
        self.root.title("Better AVL")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.scene.grid(row=0, column=0, sticky="nsew")

    def update(self, _):
        self.scene.update()

    def run(self) -> None:
        self.root.after(0, self.root.state, 'zoomed')
        self.root.mainloop()

    def set_scene(self, scene) -> None:
        from .scenes import Scene
        if not isinstance(scene, Scene): raise TypeError
        self.scene.destroy()
        self.scene = scene
        self.scene.grid(row=0, column=0, sticky="nsew")

    def after(self, ms: int, func: Callable, *args) -> None:
        self.root.after(ms, func, *args)


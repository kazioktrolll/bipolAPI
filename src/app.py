from pathlib import Path
from typing import Callable, Any, ClassVar


class App:
    def __init__(self):
        from customtkinter import CTk
        from .scenes import Scene
        from .backend.geo_design import Geometry
        self.root = CTk()
        self.scene = Scene(self)
        self.geo_path: Path
        self.mass_path: Path
        self.run_path: Path
        self.geometry: Geometry = None  # noqa Placeholder
        self.build()

    def build(self) -> None:
        self.root.title("Better AVL")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.scene.grid(row=0, column=0, sticky="nsew")

    def run(self) -> None:
        self.root.after(0, self.root.state, 'zoomed')
        self.root.mainloop()

    def set_scene(self, scene) -> None:
        from .scenes import Scene
        if not isinstance(scene, Scene): raise TypeError
        self.scene.destroy()
        self.scene = scene
        self.scene.grid(row=0, column=0, sticky="nsew")

    def after(self, ms: int, func: Callable[[Any], None], *args) -> None:
        self.root.after(ms, func, *args)


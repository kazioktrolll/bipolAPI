from pathlib import Path
from typing import Callable


class App:
    """
    The main app class that runs everything.

    Attributes:
        root (CTk): The root of the application display.
        scene (Scene): The scene currently displayed.
        geometry (Geometry): The geometry of the currently loaded plane.
        geo_path (Path): The path to the .avl geometry file.
        mass_path (Path): The path to the .mass file.
        run_path (Path): The path to the .run file.
    """
    geo_path: Path
    mass_path: Path
    run_path: Path

    def __init__(self):
        from customtkinter import CTk, set_appearance_mode, set_default_color_theme
        from .scenes import Scene
        from .backend.geo_design import Geometry
        set_appearance_mode("Dark")
        set_default_color_theme("blue")
        self.root = CTk()
        self.scene = Scene(self)  # Placeholder
        self.geometry: Geometry = Geometry(name='Plane', chord_length=1, span_length=8)  # Placeholder
        self.root.bind('<Configure>', self.update)
        self.build()

    def build(self) -> None:
        """Builds the display upon app start."""
        self.root.title("G-AVL")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.scene.grid(row=0, column=0, sticky="nsew")

    def update(self, _) -> None:
        """Updates the display."""
        self.scene.update()

    def run(self) -> None:
        """Runs the app."""
        self.after(0, self.root.state, 'zoomed')
        self.root.mainloop()

    def set_scene(self, scene) -> None:
        """Sets the Scene instance as the new currently displayed scene."""
        from .scenes import Scene
        if not isinstance(scene, Scene): raise TypeError
        self.scene.destroy()
        self.scene = scene
        self.scene.grid(row=0, column=0, sticky="nsew")

    def after(self, ms: int, func: Callable, *args) -> None:
        """Calls the given function with the given arguments after the delay given in milliseconds."""
        self.root.after(ms, func, *args)

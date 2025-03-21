from pathlib import Path
from typing import Callable
from src.backend.geo_design import Geometry


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
        set_appearance_mode("Dark")
        set_default_color_theme("blue")
        self.file_path: Path | None = None
        self.root = CTk()
        self.scene = Scene(self)  # Placeholder
        self.geometry: Geometry = Geometry(name='Plane', chord_length=1, span_length=8)  # Placeholder
        self.root.bind('<Configure>', self.update)
        self.top_bar = TopBar(self)
        self.build()

    def build(self) -> None:
        """Builds the display upon app start."""
        self.root.title("G-AVL")
        self.top_bar.grid(column=0, row=0, sticky='nsew')
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.scene.grid(row=1, column=0, sticky="nsew")

    def update(self, _=None) -> None:
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
        self.scene.grid(row=1, column=0, sticky="nsew")

    def after(self, ms: int, func: Callable, *args) -> None:
        """Calls the given function with the given arguments after the delay given in milliseconds."""
        self.root.after(ms, func, *args)

    def set_geometry(self, geometry: Geometry) -> None:
        self.geometry = geometry
        self.update()
        from src.scenes import GeoDesignScene, CalcScene
        if isinstance(self.scene, GeoDesignScene): self.scene.left_menu.update()
        if isinstance(self.scene, CalcScene): self.scene.display.update()

    # 'File' menu

    def save_as(self, path:str|Path=None) -> None:
        """Saves the current geometry as a .gavl file."""
        self.top_bar.collapse_all()
        from tkinter.filedialog import asksaveasfilename
        path = path or Path(asksaveasfilename(
            defaultextension='.gavl',
            filetypes=[('GAVL File', ['*.gavl'])],
            title=self.geometry.name
        ))
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self.geometry, f)   # noqa

    def load(self, path:str|Path=None) -> None:
        """Loads the geometry from a .gavl file."""
        self.top_bar.collapse_all()
        from tkinter.filedialog import askopenfilename
        path = path or Path(askopenfilename(
            filetypes=[('GAVL File', ['*.gavl']), ('All Files', ['*.*'])]
        ))
        import pickle
        with open(path, 'rb') as f:
            self.set_geometry(pickle.load(f))

    def new_empty(self) -> None:
        self.top_bar.collapse_all()
        from src.backend.geo_design import GeometryGenerator
        self.set_geometry(GeometryGenerator.empty())

    def new_default(self) -> None:
        self.top_bar.collapse_all()
        from src.backend.geo_design import GeometryGenerator
        self.set_geometry(GeometryGenerator.default())

    def export_to_avl(self, path:str|Path=None) -> None:
        """Exports the current geometry to an .avl file."""
        self.top_bar.collapse_all()
        from tkinter.filedialog import asksaveasfilename
        path = path or Path(asksaveasfilename(
            defaultextension='.avl',
            filetypes=[('AVL File', ['*.avl'])],
            title=self.geometry.name
        ))
        self.geometry.save_to_avl(path=path)

    def import_from_avl(self, path:str|Path=None) -> None:
        """Imports the current geometry from an .avl file."""
        from src.backend.geo_design import GeometryGenerator
        from tkinter.filedialog import askopenfilename
        self.top_bar.collapse_all()
        path = path or Path(askopenfilename(
            defaultextension='.avl',
            filetypes=[('AVL File', ['*.avl'])]
        ))
        self.set_geometry(GeometryGenerator.from_avl(path))


from customtkinter import CTkFrame


class TopBar(CTkFrame):
    def __init__(self, app:App):
        super().__init__(app.root, height=20)
        from src.frontend import TopBarItem
        TopBarItem(self, app.root, 'File', [
            ('Save', app.save_as),
            ('Load', app.load),
            ('New Empty', app.new_empty),
            ('New Default', app.new_default),
            ('Export', app.export_to_avl),
            ('Import', app.import_from_avl)
        ]).grid(column=0, row=0, sticky='nsew')
        from .scenes import GeoDesignScene, CalcScene
        TopBarItem(self, app.root, 'Workspace', [
            ('GeoDesign', lambda: app.set_scene(GeoDesignScene(app))),
            ('Calculations', lambda: app.set_scene(CalcScene(app))),
        ]).grid(column=1, row=0, sticky='nsew')

    def collapse_all(self):
        for child in self.children.values():
            try: child.collapse()   # noqa
            except AttributeError: pass

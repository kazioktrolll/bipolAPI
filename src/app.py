"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from pathlib import Path
from typing import Callable
from tempfile import TemporaryDirectory
import pickle
import os
from src.backend.geo_design import Geometry, GeometryGenerator
from src.backend import handle_crash, Settings


class App:
    """
    The main app class that runs everything.

    Attributes:
        root (CTk): The root of the application display.
        settings (Settings): The settings object that contains the permanent user preferences and previous sessions' paths.
        scene (Scene): The scene currently displayed.
        geometry (Geometry): The geometry of the currently loaded plane.
    """

    def __init__(self):
        from customtkinter import CTk, set_appearance_mode, set_default_color_theme
        from .scenes import Scene
        set_appearance_mode("Dark")
        set_default_color_theme("blue")
        self.root = CTk()
        self.settings = Settings()
        self.current_save_path: Path | None = None
        self.work_dir = TemporaryDirectory(prefix='gavl_')
        self.scene = Scene(self)  # Placeholder
        self.geometry = GeometryGenerator.empty()
        self.root.bind('<Configure>', self.update)
        self.top_bar = TopBar(self)

        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.build()

    @handle_crash
    def build(self) -> None:
        """Builds the display upon app start."""
        self.root.title("G-AVL")
        self.top_bar.grid(column=0, row=0, sticky='nsew')
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.scene.grid(row=1, column=0, sticky="nsew")

    @handle_crash
    def update(self, _=None) -> None:
        """Updates the display."""
        self.scene.update()

    @handle_crash
    def run(self) -> None:
        """Runs the app."""
        self.after(0, self.root.state, 'zoomed')
        try:
            self.root.mainloop()
        except (KeyboardInterrupt, SystemExit):
            pass

    @classmethod
    def destroy_all_children(cls, widget) -> None:
        for child in widget.winfo_children():
            App.destroy_all_children(child)
            child.destroy()

    def exit(self) -> None:
        App.destroy_all_children(self.root)
        self.root.destroy()
        self.work_dir.cleanup()

    @handle_crash
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

    @handle_crash
    def save_as(self, path: str | Path = None) -> None:
        """Saves the current geometry as a .gavl file at a path if given, otherwise opens a file dialog to choose a path."""
        self.top_bar.collapse_all()
        from tkinter.filedialog import asksaveasfilename
        path = path or Path(asksaveasfilename(
            defaultextension='.gavl',
            filetypes=[('GAVL File', ['*.gavl'])],
            title=self.geometry.name
        ))
        if path == Path('.'):
            return
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self.geometry, f)  # noqa
        self.current_save_path = path
        self.settings.data.update_recently_saved(path.as_posix())
        self.settings.save()

    @handle_crash
    def save(self) -> None:
        """Saves the current geometry as a .gavl file at the most recent save path."""
        self.save_as(self.current_save_path)

    @handle_crash
    def load(self, path: str | Path = None) -> None:
        """Loads the geometry from a .gavl file."""
        self.top_bar.collapse_all()
        from tkinter.filedialog import askopenfilename
        path = path or Path(askopenfilename(
            filetypes=[('GAVL File', ['*.gavl']), ('All Files', ['*.*'])]
        ))
        if path == Path('.'):
            return
        with open(path, 'rb') as f:
            self.set_geometry(pickle.load(f))
        self.current_save_path = path

    def new_empty(self) -> None:
        self.top_bar.collapse_all()
        from src.backend.geo_design import GeometryGenerator
        self.set_geometry(GeometryGenerator.empty())

    @handle_crash
    def new_default(self) -> None:
        self.top_bar.collapse_all()
        from src.backend.geo_design import GeometryGenerator
        self.set_geometry(GeometryGenerator.default())

    @handle_crash
    def export_to_avl(self, path: str | Path = None) -> None:
        """Exports the current geometry to an .avl file."""
        self.top_bar.collapse_all()
        from tkinter.filedialog import asksaveasfilename
        path = path or Path(asksaveasfilename(
            defaultextension='.avl',
            filetypes=[('AVL File', ['*.avl'])],
            title=self.geometry.name
        ))
        self.geometry.save_to_avl(path=path)

    @handle_crash
    def import_from_avl(self, path: str | Path = None) -> None:
        """Imports the current geometry from an .avl file."""
        from src.backend.geo_design import GeometryGenerator
        from tkinter.filedialog import askopenfilename
        self.top_bar.collapse_all()
        path = path or Path(askopenfilename(
            defaultextension='.avl',
            filetypes=[('AVL File', ['*.avl'])]
        ))
        if path == Path('.'):
            return

        geom = GeometryGenerator.from_avl(path)
        self.set_geometry(geom)

        self.set_geometry(geom)

    @staticmethod
    @handle_crash
    def open_help():
        path = Path(__file__).parent.parent / 'INSTRUCTION.pdf'
        os.startfile(path)


from customtkinter import CTkFrame
from src.frontend import TopBarItem, TopBarButton


class TopBar(CTkFrame):
    def __init__(self, app: App):
        super().__init__(app.root, height=20)
        TopBarItem(self, app.root, 'File', [
            ('Save', app.save),
            ('Save As', app.save_as),
            ('New', app.new_default),
            ('Open', app.load),
            ('Export', app.export_to_avl),
            ('Import', app.import_from_avl)
        ]).grid(column=0, row=0, sticky='nsew')
        from .scenes import GeoDesignScene, CalcScene, ValidationScene
        TopBarButton(self, 'GeoDesign', lambda: app.set_scene(GeoDesignScene(app))
                     ).grid(column=1, row=0, sticky='nsew')
        TopBarButton(self, 'Validation', lambda: app.set_scene(ValidationScene(app))
                     ).grid(column=2, row=0, sticky='nsew')
        TopBarButton(self, 'Calculations', lambda: app.set_scene(CalcScene(app))
                     ).grid(column=3, row=0, sticky='nsew')
        TopBarButton(self, 'Help', app.open_help
                     ).grid(column=4, row=0, sticky='nsew')

    def collapse_all(self):
        for child in self.children.values():
            try:
                child.collapse()  # noqa
            except AttributeError:
                pass

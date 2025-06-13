from customtkinter import CTkFrame, CTkImage, CTkEntry, CTkLabel
from pathlib import Path
from ..image_frame import ImageFrame
from ...backend.avl_interface.image_getter import ImageGetter


class ValidationDisplay(CTkFrame):
    def __init__(self, parent: CTkFrame) -> None:
        super().__init__(parent)
        self.image_frame = ImageFrame(self, ImageGetter.get_geometry(self.app.geometry, Path(self.app.work_dir.name)))
        self.build()

    def build(self) -> None:
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.image_frame.grid(row=0, column=0, sticky='nsew')

    @property
    def app(self):
        from ...scenes import Scene
        assert isinstance(self.master, Scene)
        return self.master.app

from customtkinter import CTkFrame
from pathlib import Path
from ..calcs.results_display import TextBox
from ..image_frame import ImageFrame
from ...backend.avl_interface.image_getter import ImageGetter


class ValidationDisplay(CTkFrame):
    def __init__(self, parent: CTkFrame) -> None:
        super().__init__(parent)
        self.image_frame = ImageFrame(self, ImageGetter.get_geometry(self.app.geometry, Path(self.app.work_dir.name)))
        self.data_display = TextBox(self)
        g = self.app.geometry
        self.data_display.set({
            'Reference Area\tS   =': g.surface_area * 2,
            'Reference Span\tb   =': g.span_length * 2,
            'Reference Chord\tc   =': g.chord_length,
        })
        self.build()

    def build(self) -> None:
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.image_frame.grid(row=0, column=0, sticky='nsew')
        self.data_display.grid(row=0, column=1, sticky='nsew')

    @property
    def app(self):
        from ...scenes import Scene
        assert isinstance(self.master, Scene)
        return self.master.app

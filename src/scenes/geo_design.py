from .scene import Scene
from customtkinter import CTkFrame, CTkButton
from ..frontend import GeometryDisplay


class GeoDesignScene(Scene):
    def build(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left_frame = CTkFrame(self)
        left_frame.grid(row=0, column=0, sticky='nsew')
        CTkButton(left_frame, text='text', command=self.geometry_display
                  ).grid(row=0, column=0, sticky='nsew')

        geometry_display = GeometryDisplay(self, (800,400))
        geometry_display.grid(row=0, column=1, sticky='nsew')

    @property
    def geometry_display(self):
        return self.children['!geometrydisplay']


    # TODO: Geometry creator TopLevel, pops up when GeoDesignScene is created for the first time in runtime.

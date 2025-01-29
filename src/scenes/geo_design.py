from typing import Callable

from .scene import Scene
from customtkinter import CTkFrame
from ..frontend import GeometryDisplay, ParameterField


class GeoDesignScene(Scene):
    def build(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        geometry_display = GeometryDisplay(self, self.app.geometry)
        self.to_update.append(geometry_display)
        geometry_display.grid(row=0, column=1, sticky='nsew')
        geometry_display.draw()

        left_frame = CTkFrame(self)
        left_frame.grid(row=0, column=0, sticky='nsew')

        ParameterField(left_frame, 'Add Section',
                       lambda y: self.do_with_update(self.app.geometry.wing.add_section_gentle, y)
                       ).grid(row=0, column=0, sticky='nsew')
        ParameterField(left_frame, 'Taper Ratio',
                       lambda tr: self.do_with_update(lambda tr: self.app.geometry.wing.add_section_gentle, tr)
                       ).grid(row=1, column=0, sticky='nsew')
        ParameterField(left_frame, 'Sweep Angle',
                       lambda y: self.do_with_update(self.app.geometry.wing.add_section_gentle, y)
                       ).grid(row=2, column=0, sticky='nsew')

    @property
    def geometry_display(self):
        return self.children['!geometrydisplay']

    def do_with_update(self, func: Callable, *args):
        func(*args)
        self.geometry_display.update()

from typing import Callable
from .scene import Scene
from customtkinter import CTkFrame
from ..frontend import GeometryDisplay, ParameterField
from ..backend.geo_design import Geometry, SimpleSurface


class GeoDesignScene(Scene):
    def build(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        geometry_display = GeometryDisplay(self, self.app.geometry)
        self.to_update.append(geometry_display)
        geometry_display.grid(row=0, column=1, sticky='nsew')
        geometry_display.draw()

        GeoDesignLeftMenu(self, self.app.geometry, self.geometry_display.update).grid(row=0, column=0, sticky='nsew')

    @property
    def geometry_display(self):
        return self.children['!geometrydisplay']


class GeoDesignLeftMenu(CTkFrame):
    def __init__(self, parent, geometry: Geometry, do_on_update: Callable[[], None]):
        super().__init__(parent)
        self.geometry = geometry
        self.initialized = False
        self.do_on_update = do_on_update
        wing = SimpleSurface(name='Wing', span=8, chord_length=1)
        geometry.add_surface(wing)

        messages = [
            "The wingspan of the aircraft.",
            "",
            "",
            ""
        ]

        self.pfs = {
            'wingspan': ParameterField(self, 'wingspan', help_message=messages[0], on_set=self.update_wing),
            'mean_chord': ParameterField(self, 'MAC', help_message=messages[1], on_set=self.update_wing),
            'taper': ParameterField(self, 'taper ratio', help_message=messages[2], on_set=self.update_wing),
            'sweep': ParameterField(self, 'sweep angle', help_message=messages[3], on_set=self.update_wing)
        }

        for pf in self.pfs.values(): pf.name_label.configure(width=80)

        self.pfs['wingspan'].grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.pfs['wingspan'].set(self.geometry.span_length)
        self.pfs['mean_chord'].grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.pfs['mean_chord'].set(self.geometry.chord_length)
        self.pfs['taper'].grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.pfs['taper'].set(1)
        self.pfs['sweep'].grid(row=4, column=0, padx=10, pady=10, sticky='e')
        self.pfs['sweep'].set(0)
        self.initialized = True

    def update_wing(self, _):
        if not self.initialized: return

        wing = SimpleSurface(name='Wing',
                             span=self.pfs['wingspan'].value, chord_length=self.pfs['mean_chord'].value,
                             taper_ratio=self.pfs['taper'].value, sweep_angle=self.pfs['sweep'].value)
        self.geometry.replace_surface(wing)
        self.do_on_update()

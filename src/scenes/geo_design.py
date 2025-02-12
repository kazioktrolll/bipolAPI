from typing import Callable
from customtkinter import CTkFrame
from .scene import Scene
from ..frontend import GeometryDisplay, ParameterField, ListPreset, FlapItem, ParamFromFile
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
        self.pfs: dict[str, ParameterField] = {}
        self.initialized = False
        self.do_on_update = do_on_update

        wing = SimpleSurface(name='Wing', span=8, chord_length=1)   # Placeholder, to be adjusted by User.
        geometry.add_surface(wing)
        self.init_pfs()

        self.ailerons = ListPreset(self, 'Ailerons', FlapItem, lambda: self.update_wing())
        self.ailerons.grid(row=5, column=0, padx=10, pady=10, sticky='nsew')
        self.flaps = ListPreset(self, 'Flaps', FlapItem, lambda: self.update_wing())
        self.flaps.grid(row=6, column=0, padx=10, pady=10, sticky='nsew')

        ParamFromFile(self).grid(row=7, column=0, padx=10, pady=10, sticky='nsew')

    def init_pfs(self):
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

    def update_wing(self, _=None):
        if not self.initialized: return

        wing = SimpleSurface(name='Wing',
                             span=self.pfs['wingspan'].value, chord_length=self.pfs['mean_chord'].value,
                             taper_ratio=self.pfs['taper'].value, sweep_angle=self.pfs['sweep'].value)
        wing.set_mechanization(ailerons=self.ailerons.get_values(), flaps=self.flaps.get_values()) # noqa The types match.
        self.geometry.replace_surface(wing)
        self.do_on_update()

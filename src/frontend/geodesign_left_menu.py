from customtkinter import CTkFrame
from .parameter_field import ParameterField
from ..backend.geo_design import Wing, Geometry
from typing import Callable


class GeoDesignLeftMenu(CTkFrame):
    def __init__(self, parent, geometry: Geometry, do_on_update: Callable[[], None]):
        super().__init__(parent)
        self.geometry = geometry
        self.initialized = False
        self.do_on_update = do_on_update
        wing = Wing(wingspan=8, chord_length=1)
        geometry.add_surface(wing)

        self.pfs = {
            'wingspan': ParameterField(self, 'wingspan', on_set=self.update_wing),
            'mean_chord': ParameterField(self, 'MAC', on_set=self.update_wing),
            'taper': ParameterField(self, 'taper ratio', on_set=self.update_wing),
            'sweep': ParameterField(self, 'sweep angle', on_set=self.update_wing)
        }

        for pf in self.pfs.values(): pf.name_label.configure(width=70)

        self.pfs['wingspan'].grid_def(row=0, column=0)
        self.pfs['wingspan'].set(self.geometry.span_length)
        self.pfs['mean_chord'].grid_def(row=1, column=0)
        self.pfs['mean_chord'].set(self.geometry.chord_length)
        self.pfs['taper'].grid_def(row=3, column=0)
        self.pfs['taper'].set(1)
        self.pfs['sweep'].grid_def(row=4, column=0)
        self.pfs['sweep'].set(0)
        self.initialized = True

    def update_wing(self, _):
        if not self.initialized: return
        self.geometry.span_length = self.pfs['wingspan'].value
        self.geometry.chord_length = self.pfs['mean_chord'].value

        wing = Wing(wingspan=self.pfs['wingspan'].value, chord_length=self.pfs['mean_chord'].value,
                    taper_ratio=self.pfs['taper'].value, sweep_angle=self.pfs['sweep'].value)
        self.geometry.replace_surface(wing)
        self.do_on_update()

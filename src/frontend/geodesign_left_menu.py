from customtkinter import CTkFrame
from .parameter_field import ParameterField


class GeoDesignLeftMenu(CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.pfs = {
            'wingspan': ParameterField(self, 'wingspan', on_set=self.init_wing),
            'mean_chord': ParameterField(self, 'MAC', on_set=self.init_wing),
            'surface': ParameterField(self, 'wing reference area'),
            'taper': ParameterField(self, 'taper ratio'),
            'sweep': ParameterField(self, 'sweep angle')
        }

        for pf in self.pfs.values(): pf.name_label.configure(width=120)

        self.pfs['wingspan'].grid_def(row=0, column=0)
        self.pfs['mean_chord'].grid_def(row=1, column=0)

    def init_wing(self, _):
        """Initialize wing object given wingspan and mean chord."""
        if self.pfs['wingspan'].value == 0: return
        if self.pfs['mean_chord'].value == 0: return

        self.pfs['wingspan'].disable()
        self.pfs['mean_chord'].disable()

        self.pfs['surface'].grid_def(row=2, column=0)
        self.pfs['surface'].entry.insert(0, self.pfs['wingspan'].value * self.pfs['mean_chord'].value)
        self.pfs['taper'].grid_def(row=3, column=0)
        self.pfs['taper'].set(1)
        self.pfs['sweep'].grid_def(row=4, column=0)

from customtkinter import CTkFrame, CTkButton
from typing import Callable

from .airfoil_chooser import AirfoilChooser
from ..parameter_field import ParameterField
from ..items import FlapItem
from ..list_preset import ListPreset
from ...backend.geo_design import Geometry, SimpleSurface


class GeoDesignLeftMenu(CTkFrame):
    def __init__(self, parent, geometry: Geometry, do_on_update: Callable[[], None]):
        super().__init__(parent)
        self.geometry = geometry
        self.pfs: dict[str, ParameterField] = {}
        self.initialized = False
        self.do_on_update = do_on_update

        wing = SimpleSurface(name='Wing', span=8, chord_length=1)   # Placeholder, to be adjusted by User.
        geometry.add_surface(wing)
        self.pf_frame = CTkFrame(self, fg_color=self.cget('fg_color'))
        self.pf_frame.grid(row=0, column=0, sticky='nsew')
        self.init_pfs()

        self.ailerons = ListPreset(self, 'Ailerons', FlapItem, lambda: self.update_wing())
        self.ailerons.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.flaps = ListPreset(self, 'Flaps', FlapItem, lambda: self.update_wing())
        self.flaps.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

        self.airfoil_chooser = AirfoilChooser(self)
        self.airfoil_chooser.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')

        CTkButton(self, text="Save to File", command=self.save_to_file
                  ).grid(row=4, column=0, padx=10, pady=10, sticky='nsew')

    def init_pfs(self):
        messages = [
            "The wingspan of the aircraft.",
            "",
            "",
            "",
            ""
        ]

        self.pfs = {
            'wingspan': ParameterField(self.pf_frame, 'wingspan', help_message=messages[0], on_set=self.update_wing),
            'mean_chord': ParameterField(self.pf_frame, 'MAC', help_message=messages[1], on_set=self.update_wing),
            'taper': ParameterField(self.pf_frame, 'taper ratio', help_message=messages[2], on_set=self.update_wing),
            'sweep': ParameterField(self.pf_frame, 'sweep angle', help_message=messages[3], on_set=self.update_wing),
            'cm_pos': ParameterField(self.pf_frame, 'CM Position', help_message=messages[4], on_set=self.update_wing)
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
        self.pfs['cm_pos'].grid(row=5, column=0, padx=10, pady=10, sticky='e')
        self.initialized = True

    def update_wing(self, _=None):
        if not self.initialized: return

        wing = SimpleSurface(name='Wing',
                             span=self.pfs['wingspan'].value, chord_length=self.pfs['mean_chord'].value,
                             taper_ratio=self.pfs['taper'].value, sweep_angle=self.pfs['sweep'].value,
                             origin_position=(-self.pfs['cm_pos'].value * self.pfs['mean_chord'].value, 0, 0),
                             airfoil=self.airfoil_chooser.airfoil)
        wing.set_mechanization(ailerons=self.ailerons.get_values(), flaps=self.flaps.get_values()) # noqa The types match.
        self.geometry.replace_surface(wing)
        self.do_on_update()

    def save_to_file(self):
        from pathlib import Path
        from tkinter import filedialog
        self.update_wing()
        path = Path(filedialog.asksaveasfilename(confirmoverwrite=True,
                                                 initialfile=f"{self.geometry.name}.avl",
                                                 defaultextension='.avl',
                                                 filetypes=[("AVL file", "*.avl"), ("All files", "*.*")]))
        self.geometry.save_to_avl(self.geometry.name, path)
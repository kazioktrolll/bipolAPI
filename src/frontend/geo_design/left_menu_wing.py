from customtkinter import CTkFrame, CTkButton
from typing import Callable

from .airfoil_chooser import AirfoilChooser
from ..parameter_field import ParameterField
from ..items import FlapItem
from ..list_preset import ListPreset
from ..help_top_level import HelpTopLevel
from ...backend.geo_design import Geometry, SimpleSurface


class LeftMenuWing(CTkFrame):
    def __init__(self, parent, do_on_update: Callable[[], None]):
        super().__init__(parent)
        self.pfs: dict[str, ParameterField] = {}
        self.initialized = False
        self.do_on_update = do_on_update

        wing = SimpleSurface(name='Wing', span=8, chord_length=1)   # Placeholder, to be adjusted by User.
        self.geometry.add_surface(wing)
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

    @property
    def geometry(self) -> Geometry:
        from .left_menu_general import LeftMenu
        assert isinstance(self.master, LeftMenu)
        return self.master.geometry

    def init_pfs(self):
        messages = [
            "The wingspan of the aircraft.\n"
            "Has to be positive.",

            "The mean aerodynamic chord of the wing.\n"
            "Has to be positive.",

            "The taper ratio of the wing - c_tip / c_root.\n"
            "Has to be between 0 and 1.",

            "Sweep angle of the wing, in degrees.\n"
            "The angle between Y-axis and the 25%MAC line. Positive means wing deflected backwards.\n"
            "Has to be between -90 and 90.",

            "Position of the Center of Mass of the aircraft relative to MAC, given as a fraction of MAC.\n"
            "This will affect the calculations of the pitching moment coefficient, as C_M is calculated about CoM."
        ]

        self.pfs = {
            'wingspan': ParameterField(self.pf_frame, 'wingspan', help_message=messages[0], on_set=self.update_wing, assert_test=lambda w: w>0),
            'mean_chord': ParameterField(self.pf_frame, 'MAC', help_message=messages[1], on_set=self.update_wing, assert_test=lambda c: c>0),
            'taper': ParameterField(self.pf_frame, 'taper ratio', help_message=messages[2], on_set=self.update_wing, assert_test=lambda tr: 1>=tr>0),
            'sweep': ParameterField(self.pf_frame, 'sweep angle', help_message=messages[3], on_set=self.update_wing, assert_test=lambda s: -90<s<90),
            'cm_pos': ParameterField(self.pf_frame, 'CM Position', help_message=messages[4], on_set=self.update_wing, assert_test=lambda cm: True)
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
        try:
            wing.set_mechanization(ailerons=self.ailerons.get_values(), flaps=self.flaps.get_values()) # noqa
        except ValueError:
            HelpTopLevel(self, "Can't have multiple control surfaces intersecting!\n"
                               "If your control surfaces intersect, please don't.\n"
                               "If your control surfaces don't intersect, but one ends in the same point the next starts, give them a little space in between.")
            return
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
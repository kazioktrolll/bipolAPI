from customtkinter import CTkFrame
from typing import Callable

from .airfoil_chooser import AirfoilChooser
from ..parameter_field import ParameterField
from ..items import FlapItem
from ..list_preset import ListPreset
from ...backend.geo_design import Geometry, SimpleSurface


class LeftMenuHTail(CTkFrame):
    def __init__(self, parent, geometry: Geometry, do_on_update: Callable[[], None]):
        super().__init__(parent)
        self.geometry = geometry
        self.pfs: dict[str, ParameterField] = {}
        self.initialized = False
        self.do_on_update = do_on_update

        h_tail = SimpleSurface(name='H_tail', span=2, chord_length=.5, origin_position=(4, 0, 1))   # Placeholder, to be adjusted by User.
        geometry.add_surface(h_tail)
        self.pf_frame = CTkFrame(self, fg_color=self.cget('fg_color'))
        self.pf_frame.grid(row=0, column=0, sticky='nsew')
        self.init_pfs()

        self.elevator = ListPreset(self, 'Elevator', FlapItem, lambda: self.update_tail())
        self.elevator.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        self.airfoil_chooser = AirfoilChooser(self)
        self.airfoil_chooser.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')

    def init_pfs(self):
        messages = [
            "Position of the horizontal tail along X-axis.\n"
            "The horizontal distance between the leading edges of the root chords of the wing and the horizontal tail.",

            "Position of the horizontal tail along Z-axis.\n"
            "The vertical distance between the leading edges of the root chords of the wing and the horizontal tail.",

            "The span of the horizontal tail.\n"
            "Has to be positive.",

            "The mean aerodynamic chord of the horizontal tail.\n"
            "Has to be positive.",

            "The taper ratio of the horizontal tail - c_tip / c_root.\n"
            "Has to be between 0 and 1.",

            "Sweep angle of the horizontal tail, in degrees.\n"
            "The angle between Y-axis and the 25%MAC line. Positive means horizontal tail deflected backwards.\n"
            "Has to be between -90 and 90."
        ]

        self.pfs = {
            'x': ParameterField(self.pf_frame, 'x', help_message=messages[0], on_set=self.update_tail, assert_test=lambda w: True),
            'z': ParameterField(self.pf_frame, 'z', help_message=messages[1], on_set=self.update_tail, assert_test=lambda w: True),
            'span': ParameterField(self.pf_frame, 'wingspan', help_message=messages[2], on_set=self.update_tail, assert_test=lambda w: w > 0),
            'mean_chord': ParameterField(self.pf_frame, 'MAC', help_message=messages[3], on_set=self.update_tail, assert_test=lambda c: c > 0),
            'taper': ParameterField(self.pf_frame, 'taper ratio', help_message=messages[4], on_set=self.update_tail, assert_test=lambda tr: 1 >= tr > 0),
            'sweep': ParameterField(self.pf_frame, 'sweep angle', help_message=messages[5], on_set=self.update_tail, assert_test=lambda s: -90 < s < 90),
        }

        for pf in self.pfs.values(): pf.name_label.configure(width=80)

        self.pfs['x'].grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.pfs['x'].set(self.geometry.h_tail.origin_position[0])
        self.pfs['z'].grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.pfs['z'].set(self.geometry.h_tail.origin_position[2])
        self.pfs['span'].grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.pfs['span'].set(self.geometry.h_tail.span())
        self.pfs['mean_chord'].grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.pfs['mean_chord'].set(self.geometry.h_tail.chord_length)
        self.pfs['taper'].grid(row=4, column=0, padx=10, pady=10, sticky='e')
        self.pfs['taper'].set(1)
        self.pfs['sweep'].grid(row=5, column=0, padx=10, pady=10, sticky='e')
        self.pfs['sweep'].set(0)
        self.initialized = True

    def update_tail(self, _=None):
        if not self.initialized: return

        h_tail = SimpleSurface(name='H_tail',
                               span=self.pfs['span'].value, chord_length=self.pfs['mean_chord'].value,
                               taper_ratio=self.pfs['taper'].value, sweep_angle=self.pfs['sweep'].value,
                               origin_position=(self.pfs['x'].value, 0, self.pfs['z'].value),
                               airfoil=self.airfoil_chooser.airfoil)
        h_tail.set_mechanization(elevators=self.elevator.get_values()) # noqa The types match.
        self.geometry.replace_surface(h_tail)
        self.do_on_update()

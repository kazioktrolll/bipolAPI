from customtkinter import CTkFrame
from typing import Callable

from .airfoil_chooser import AirfoilChooser
from ..parameter_field import ParameterField
from ..items import FlapItem
from ..list_preset import ListPreset
from ...backend.geo_design import Geometry, VerticalSurface, Section, Airfoil


class LeftMenuVTail(CTkFrame):
    def __init__(self, parent, geometry: Geometry, do_on_update: Callable[[], None]):
        super().__init__(parent)
        self.geometry = geometry
        self.pfs: dict[str, ParameterField] = {}
        self.initialized = False
        self.do_on_update = do_on_update

        h_tail = VerticalSurface(name="V_tail", chord_length=.4,
                                 root_section=Section(leading_edge_position=(0,0,0), chord=.5, inclination=0, airfoil=Airfoil.empty()),
                                 tip_section=Section(leading_edge_position=(.3,0,.5), chord=.3, inclination=0, airfoil=Airfoil.empty()),
                                 y_duplicate=False, origin_position=(3.7,0,.5), airfoil=Airfoil.empty())   # Placeholder, to be adjusted by User.
        geometry.add_surface(h_tail)
        self.pf_frame = CTkFrame(self, fg_color=self.cget('fg_color'))
        self.pf_frame.grid(row=0, column=0, sticky='nsew')
        self.init_pfs()

        self.v_stabilizer = ListPreset(self, 'Vertical Stabilizer', FlapItem, lambda: self.update_tail())
        self.v_stabilizer.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        self.airfoil_chooser = AirfoilChooser(self)
        self.airfoil_chooser.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')

    def init_pfs(self):
        messages = [
            "Position of the vertical tail along X-axis.\n"
            "The horizontal distance between the leading edges of the root chords of the wing and the vertical tail.",

            "Position of the vertical tail along Z-axis.\n"
            "The vertical distance between the leading edges of the root chords of the wing and the vertical tail.",

            "The height of the vertical tail.\n"
            "Has to be positive.",

            "The aerodynamic chord of the root of the vertical tail.\n"
            "Has to be positive.",

            "The aerodynamic chord of the tip of the vertical tail.\n"
            "Has to be positive.",

            "X-axis distance between the tip of root and tip sections.\n"
        ]

        self.pfs = {
            'x': ParameterField(self.pf_frame, 'x', help_message=messages[0], on_set=self.update_tail, assert_test=lambda w: True),
            'z': ParameterField(self.pf_frame, 'z', help_message=messages[1], on_set=self.update_tail, assert_test=lambda w: True),
            'height': ParameterField(self.pf_frame, 'height', help_message=messages[2], on_set=self.update_tail, assert_test=lambda w: w > 0),
            'root_chord': ParameterField(self.pf_frame, 'Root Chord', help_message=messages[3], on_set=self.update_tail, assert_test=lambda c: c > 0),
            'tip_chord': ParameterField(self.pf_frame, 'Tip Chord', help_message=messages[4], on_set=self.update_tail, assert_test=lambda c: c > 0),
            'x_offset': ParameterField(self.pf_frame, 'Tip x offset', help_message=messages[5], on_set=self.update_tail, assert_test=lambda c: True)
        }

        for pf in self.pfs.values(): pf.name_label.configure(width=80)

        self.pfs['x'].grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.pfs['x'].set(self.geometry.v_tail.origin_position[0])
        self.pfs['z'].grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.pfs['z'].set(self.geometry.v_tail.origin_position[2])
        self.pfs['height'].grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.pfs['height'].set(self.geometry.v_tail.span())
        self.pfs['root_chord'].grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.pfs['root_chord'].set(self.geometry.v_tail.sections[0].chord)
        self.pfs['tip_chord'].grid(row=4, column=0, padx=10, pady=10, sticky='e')
        self.pfs['tip_chord'].set(self.geometry.v_tail.sections[-1].chord)
        self.pfs['x_offset'].grid(row=5, column=0, padx=10, pady=10, sticky='e')
        self.pfs['x_offset'].set(self.geometry.v_tail.sections[-1].x)
        self.initialized = True

    def update_tail(self, _=None):
        if not self.initialized: return

        h_tail = VerticalSurface(name="V_tail",
                                 chord_length=self.pfs['mean_chord'].value,
                                 root_section=Section(leading_edge_position=(0,0,0),
                                                      chord=self.pfs['root_chord'].value,
                                                      inclination=0, airfoil=Airfoil.empty()),
                                 tip_section=Section(leading_edge_position=(self.pfs['x_offset'].value, 0, self.pfs['height'].value),
                                                     chord=self.pfs['tip_chord'].value,
                                                     inclination=0, airfoil=Airfoil.empty()),
                                 y_duplicate=False,
                                 origin_position=(self.pfs['x'].value, 0, self.pfs['z'].value),
                                 airfoil=Airfoil.empty())

        # h_tail.set_mechanization(elevators=self.v_stabilizer.get_values()) # noqa The types match.
        self.geometry.replace_surface(h_tail)
        self.do_on_update()

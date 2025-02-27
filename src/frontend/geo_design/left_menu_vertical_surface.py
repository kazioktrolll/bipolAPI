from .left_menu_item import LeftMenuItem
from ...backend.geo_design import VerticalSurface, Section


class LeftMenuVerticalSurface(LeftMenuItem):
    def __init__(self, parent, surface: VerticalSurface) -> None:
        super().__init__(parent, surface)

    def init_pfs(self) -> None:
        # keyword, name, message, assert, initial
        pfs_params = [
            ('x', 'X', "Position of the surface along X-axis.\n"
                       "The horizontal distance between the leading edges of the root chords of the wing and the vertical tail.",
             lambda x: True, self.surface.origin_position.x),

            ('z', 'Z', "Position of the vertical tail along Z-axis.\n"
                       "The vertical distance between the leading edges of the root chords of the wing and the vertical tail.",
             lambda z: True, self.surface.origin_position.z),

            ('height', 'Height', "The height of the surface.\n",
             lambda h: True, self.surface.span()),

            ('root_chord', "Root Chord", "The aerodynamic chord of the root of the vertical tail.\n"
                                         "Has to be positive.",
             lambda rc: rc > 0, self.surface.sections[0].chord),

            ('tip_chord', "Tip Chord", "The aerodynamic chord of the tip of the vertical tail.\n"
                                       "Has to be positive.",
             lambda rc: rc > 0, self.surface.sections[-1].chord),

            ('x_offset', "X Offset", "X-axis distance between the tip of root and tip sections.\n",
             lambda xo: True, self.surface.sections[-1].leading_edge_position.x),
        ]
        for pf_params in pfs_params: super()._init_pf(*pf_params)
        super().init_pfs()

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: VerticalSurface(
            name=self.name,
            chord_length=(self.pfs['root_chord'].value + self.pfs['tip_chord'].value)/2,
            sections = [
                Section(
                    leading_edge_position=(0, 0, 0),
                    chord=self.pfs['root_chord'].value, inclination=0,
                    airfoil=self.airfoil_chooser.airfoil
                ),
                Section(
                    leading_edge_position=(self.pfs['x_offset'].value, 0, self.pfs['height'].value),
                    chord=self.pfs['tip_chord'].value, inclination=0,
                    airfoil=self.airfoil_chooser.airfoil
                )
            ],
            origin_position=(
                self.pfs['x'].value,
                0,
                self.pfs['z'].value
            ),
            airfoil=self.airfoil_chooser.airfoil,
            y_duplicate=False
        )
        mechs = {name: lp.get_values() for name, lp in self.mechanizations.items()}
        super()._update_surface(surface_generator)

    @classmethod
    def default(cls, parent, name: str) -> 'LeftMenuVerticalSurface':
        surface = VerticalSurface(
            name=name,
            chord_length=1,
            sections = [
                Section(
                    leading_edge_position=(0, 0, 0),
                    chord=1, inclination=0
                ),
                Section(
                    leading_edge_position=(.2, 0, 1),
                    chord=.9, inclination=0
                )
            ],
            origin_position=(0, 0, 0),
            y_duplicate=False
        )
        from .left_menu import LeftMenu
        assert isinstance(parent, LeftMenu)
        parent.geometry.add_surface(surface)
        return cls(parent, surface)

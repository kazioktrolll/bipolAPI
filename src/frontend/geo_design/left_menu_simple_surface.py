from .left_menu_item import LeftMenuItem
from ...backend.geo_design import SimpleSurface


class LeftMenuSimpleSurface(LeftMenuItem):
    def __init__(self, parent, surface: SimpleSurface):
        super().__init__(parent, surface)

    def init_pfs(self) -> None:
        # keyword, name, message, assert, initial
        pfs_params = [
            ('x', 'X', 'The X-axis position of the tip of the root section.', lambda x: True, 0),
            ('z', 'Z', 'The Z-axis position of the tip of the root section.', lambda z: True, 0),
            ('span', 'Span', "The span of the horizontal tail.\nHas to be positive.", lambda w: w > 0, 4),
            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.", lambda c: c > 0, 1),
            ('taper', 'Taper Ratio', "The taper ratio of the surface - c_tip / c_root.\nHas to be between 0 and 1.", lambda tr: 0 <= tr <= 1, 1),
            ('sweep', 'Sweep Angle', "Sweep angle of the wing, in degrees.\n"
                                     "The angle between Y-axis and the 25%MAC line. Positive means wing deflected backwards.\n"
                                     "Has to be between -90 and 90.", lambda sa: -90 < sa < 90, 0),
            ('inclination', 'Inclination', "The inclination of the surface, in degrees\n.", lambda i: True, 0)
        ]
        for pf_params in pfs_params: super()._init_pf(*pf_params)
        super().init_pfs()

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: SimpleSurface(
            name=self.name,
            span=self.pfs['span'].value,
            chord_length=self.pfs['chord'].value,
            taper_ratio=self.pfs['taper'].value,
            sweep_angle=self.pfs['sweep'].value,
            origin_position=(
                self.pfs['x'].value,
                0,
                self.pfs['z'].value
            ),
            inclination_angle=self.pfs['inclination'].value,
            airfoil=self.airfoil_chooser.airfoil
        )
        mechs = {name: lp.get_values() for name, lp in self.mechanizations.items()}
        do_with_surface = lambda surface: surface.set_mechanization(**mechs)
        super()._update_surface(surface_generator, do_with_surface)

    @classmethod
    def default(cls, parent, name: str) -> 'LeftMenuSimpleSurface':
        surface = SimpleSurface(
            name=name,
            span=4,
            chord_length=1
        )
        from .left_menu import LeftMenu
        assert(isinstance(parent, LeftMenu))
        parent.geometry.add_surface(surface)
        return cls(parent, surface)

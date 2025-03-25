from customtkinter import StringVar
from .left_menu_item import LeftMenuItem
from .mechanization_chooser import ListPresetItem
from .. import FlapItem
from ...backend.geo_design import HorizontalSimpleSurface


class LeftMenuSimpleSurface(LeftMenuItem):
    def __init__(self, parent, surface: HorizontalSimpleSurface):
        super().__init__(parent, surface)
        self.build()

    def init_pfs(self) -> None:
        # keyword, name, message, assert, initial
        surf = self.surface
        assert isinstance(surf, HorizontalSimpleSurface)    # for type checker
        pfs_params = [
            ('x', 'X', 'The X-axis position of the tip of the root section.',
             lambda x: True, surf.origin_position.x),

            ('z', 'Z', 'The Z-axis position of the tip of the root section.',
             lambda z: True, surf.origin_position.z),

            ('span', 'Span', "The span of the horizontal tail.\nHas to be positive.",
             lambda w: w > 0, surf.span()),

            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.",
             lambda c: c > 0, surf.mac()),

            ('taper', 'Taper Ratio', "The taper ratio of the surface - c_tip / c_root.\nHas to be between 0 and 1.",
             lambda tr: 0 <= tr <= 1, surf.taper_ratio),

            ('sweep', 'Sweep Angle', "Sweep angle of the wing, in degrees.\n"
                                     "The angle between Y-axis and the 25%MAC line. Positive means wing deflected backwards.\n"
                                     "Has to be between -90 and 90.",
             lambda sa: -90 < sa < 90, surf.sweep_angle),

            ('inclination', 'Inclination', "The inclination of the surface, in degrees\n.",
             lambda i: True, surf.inclination)
        ]
        for pf_params in pfs_params: super()._init_pf(*pf_params)
        super().init_pfs()

    def init_mechanization(self):
        assert isinstance(self.surface, HorizontalSimpleSurface)
        if not self.surface.mechanization: return
        for key, list_of_ranges in self.surface.mechanization.items():
            key = key.capitalize()
            list_preset = ListPresetItem(key, self.update_surface)
            for start, stop, xc in list_of_ranges:
                item = FlapItem()
                item.set_values(StringVar(value=f'{start}'), StringVar(value=f'{stop}'), StringVar(value=f'{xc}'))
                list_preset.add_position(item)
            self.mechanizations.add_position((key, list_preset))

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: HorizontalSimpleSurface(
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
        do_with_surface = lambda surface: surface.set_mechanization(**self.mechanizations.get_values())
        super()._update_surface(surface_generator, do_with_surface)

    @classmethod
    def default(cls, parent, name: str) -> 'LeftMenuSimpleSurface':
        surface = HorizontalSimpleSurface(
            name=name,
            span=4,
            chord_length=1
        )
        from .left_menu import LeftMenu
        assert(isinstance(parent, LeftMenu))
        parent.geometry.add_surface(surface)
        return cls(parent, surface)

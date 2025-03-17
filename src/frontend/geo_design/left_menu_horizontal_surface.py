from .left_menu_item import LeftMenuItem
from ..list_preset import ListPreset
from ..items import SectionItem
from ...backend.geo_design import HorizontalSurface


class LeftMenuHorizontalSurface(LeftMenuItem):
    def __init__(self, parent, surface: HorizontalSurface):
        super().__init__(parent, surface)
        self.sections_list = ListPreset(self, 'Sections', SectionItem, self.update_surface)
        for sect in self.surface.sections: self.sections_list.add_position(SectionItem.from_section(sect))
        self.build()

    def build(self) -> None:
        for i, mech in enumerate(self.mechanizations.values()):
            mech.grid(row=i, column=0, padx=10, pady=10, sticky='nsew')

        self.columnconfigure(0, weight=1)

        self.pf_frame.grid(row=0, column=0, sticky='nsew')
        self.sections_list.grid(row=1, column=0, sticky='nsew')
        self.mechanizations_frame.grid(row=2, column=0, sticky='nsew')
        self.airfoil_chooser.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')

    def init_pfs(self) -> None:
        # keyword, name, message, assert, initial
        surf = self.surface
        assert isinstance(surf, HorizontalSurface)
        pfs_params = [
            ('x', 'X', 'The X-axis position of the tip of the root section.', lambda x: True, surf.origin_position.x),
            ('y', 'Y', 'The Y-axis position of the tip of the root section.', lambda y: True, surf.origin_position.y),
            ('z', 'Z', 'The Z-axis position of the tip of the root section.', lambda z: True, surf.origin_position.z),
            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.", lambda c: c > 0, surf.chord_length),
            ('y_duplicate', 'Y-symmetric', "", lambda y: y in (0, 1), int(surf.y_duplicate)),
        ]
        for pf_params in pfs_params: super()._init_pf(*pf_params)
        super().init_pfs()

    def update_surface(self, _=None) -> None:
        pass

from .left_menu_item import LeftMenuItem
from .. import Item
from ..list_preset import ListPreset
from ..items import SectionItem
from ...backend.geo_design import HorizontalSurface, Section


class LeftMenuHorizontalSurface(LeftMenuItem):
    def __init__(self, parent, surface: HorizontalSurface):
        super().__init__(parent, surface)
        self.sections_list = SectionsListPreset(self, self.surface.sections)
        self.airfoil_chooser.set(self.surface.airfoil)
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
            ('y_duplicate', 'Y-symmetric', "", lambda y: y in (0, 1), int(surf.y_duplicate)),
        ]
        for pf_params in pfs_params: super()._init_pf(*pf_params)
        super().init_pfs()

    def get_sections(self) -> list[Section]:
        sections = []
        for tup in self.sections_list.get_values():
            pos, chord, inc, control = tup
            sections.append(Section(leading_edge_position=pos, chord=chord, inclination=inc, airfoil=self.airfoil_chooser.airfoil, control=control))
        return sections

    def update_surface(self, _=None) -> None:
        surface_getter = lambda: HorizontalSurface(
            name=self.surface.name,
            sections=self.get_sections(),
            y_duplicate=bool(self.pfs['y_duplicate'].value),
            origin_position=(self.pfs['x'].value, self.pfs['y'].value, self.pfs['z'].value),
            airfoil=self.airfoil_chooser.airfoil
        )
        super()._update_surface(surface_getter)
        pass


class SectionsListPreset(ListPreset):
    def __init__(self, parent: LeftMenuHorizontalSurface, sections: list[Section]):
        super().__init__(parent, 'Sections', SectionItem, parent.update_surface)
        for sect in sections: self.add_position(SectionItem.from_section(sect))

    def sort(self):
        self.item_frames.sort(key=lambda i_f: i_f.item.y.get())
        for child in self.body_frame.children.values(): child.grid_forget()
        for i, frame in enumerate(self.item_frames):
            frame.locked = False
            frame.grid(column=0, row=i, sticky="nsew")
        self.item_frames[0].locked = True
        self.item_frames[-1].locked = True
        self.update_items()

    def add_position(self, item: Item = None) -> None:
        super().add_position(item)
        self.sort()

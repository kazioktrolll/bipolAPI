"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from .left_menu_item import LeftMenuItem
from ....backend.geo_design import Surface


class LMRectangularV(LeftMenuItem):
    @property
    def active_pfs(self) -> list[str]:
        return ['pos', 'span', 'height', 'chord']

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: Surface.template.simple_tapered(
            name=self.name,
            length=self.pfs['height'].value,
            chord=self.pfs['chord'].value,
            origin_position=(
                self.pfs['pos'].value[0],
                0,
                self.pfs['pos'].value[1]
            ),
            airfoil=self.airfoil_chooser.airfoil,
            taper_ratio=1,
            sweep_angle=0,
            inclination_angle=0,
            dihedral_angle=90,
            mid_gap=0
        )
        super()._update_surface(surface_generator)


class LMSimpleTaperedV(LeftMenuItem):
    @property
    def active_pfs(self) -> list[str]:
        return ['pos', 'height', 'chord', 'taper', 'sweep']

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: Surface.template.simple_tapered(
            name=self.name,
            length=self.pfs['height'].value,
            chord=self.pfs['chord'].value,
            taper_ratio=self.pfs['taper'].value,
            sweep_angle=self.pfs['sweep'].value,
            origin_position=(
                self.pfs['pos'].value[0],
                0,
                self.pfs['pos'].value[1]
            ),
            airfoil=self.airfoil_chooser.airfoil,
            inclination_angle=0,
            dihedral_angle=90,
            mid_gap=0
        )
        super()._update_surface(surface_generator)


class LMTwinV(LeftMenuItem):
    @property
    def active_pfs(self) -> list[str]:
        return ['pos', 'height', 'chord', 'taper', 'sweep', 'gap']

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: Surface.template.simple_tapered(
            name=self.name,
            length=self.pfs['height'].value,
            chord=self.pfs['chord'].value,
            taper_ratio=self.pfs['taper'].value,
            sweep_angle=self.pfs['sweep'].value,
            origin_position=(
                self.pfs['pos'].value[0],
                0,
                self.pfs['pos'].value[1]
            ),
            airfoil=self.airfoil_chooser.airfoil,
            mid_gap=self.pfs['gap'].value,
            inclination_angle=0,
            dihedral_angle=90
        )
        super()._update_surface(surface_generator)

"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from .left_menu_item import LeftMenuItem
from ....backend.geo_design import Surface


class LMTapered(LeftMenuItem):
    @property
    def active_pfs(self) -> list[str]:
        return ['pos', 'span', 'chord', 'taper', 'sweep', 'inclination', 'dihedral']

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: Surface.template.simple_tapered(
            name=self.name,
            length=self.pfs['span'].value/2,
            chord=self.pfs['chord'].value,
            taper_ratio=self.pfs['taper'].value,
            sweep_angle=self.pfs['sweep'].value,
            origin_position=(
                self.pfs['pos'].value[0],
                0,
                self.pfs['pos'].value[1]
            ),
            inclination_angle=self.pfs['inclination'].value,
            dihedral_angle=self.pfs['dihedral'].value,
            airfoil=self.airfoil_chooser.airfoil,
            mid_gap=0
        )
        super()._update_surface(surface_generator)


class LMRectangular(LeftMenuItem):
    @property
    def active_pfs(self) -> list[str]:
        return ['pos', 'span', 'chord', 'inclination']

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: Surface.template.simple_tapered(
            name=self.name,
            length=self.pfs['span'].value/2,
            chord=self.pfs['chord'].value,
            origin_position=(
                self.pfs['pos'].value[0],
                0,
                self.pfs['pos'].value[1]
            ),
            inclination_angle=self.pfs['inclination'].value,
            airfoil=self.airfoil_chooser.airfoil,
            taper_ratio=1,
            sweep_angle=0,
            mid_gap=0,
            dihedral_angle=0
        )
        super()._update_surface(surface_generator)


class LMDelta(LeftMenuItem):
    @property
    def active_pfs(self) -> list[str]:
        return ['pos', 'span', 'surface_area', 'inclination']

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: Surface.template.delta(
            name=self.name,
            span=self.pfs['span'].value,
            surface_area=self.pfs['surface_area'].value,
            origin_position=(
                self.pfs['pos'].value[0],
                0,
                self.pfs['pos'].value[1]
            ),
            inclination_angle=self.pfs['inclination'].value,
            airfoil=self.airfoil_chooser.airfoil
        )
        super()._update_surface(surface_generator)


class LMDoubleTrapez(LeftMenuItem):
    @property
    def active_pfs(self) -> list[str]:
        return ['pos', 'root_chord', 'mid_chord', 'tip_chord', 'span', 'ss', 'inclination', 'sweep', 'dihedral']

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: Surface.template.double_trapez(
            name=self.name,
            root_chord=self.pfs['root_chord'].value,
            mid_chord=self.pfs['mid_chord'].value,
            tip_chord=self.pfs['tip_chord'].value,
            length=self.pfs['span'].value/2,
            seam_spanwise=self.pfs['ss'].value * self.pfs['span'].value / 2,
            sweep_angle=self.pfs['sweep'].value,
            origin_position=(
                self.pfs['pos'].value[0],
                0,
                self.pfs['pos'].value[1]
            ),
            inclination_angle=self.pfs['inclination'].value,
            dihedral_angle=self.pfs['dihedral'].value,
            airfoil=self.airfoil_chooser.airfoil,
            mid_gap=0
        )
        super()._update_surface(surface_generator)

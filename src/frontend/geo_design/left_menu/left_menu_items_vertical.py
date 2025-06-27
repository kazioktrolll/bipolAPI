"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from functools import cached_property
from typing import Any, Callable
from .left_menu_item import LeftMenuItem
from ....backend.geo_design import Surface


class LMRectangularV(LeftMenuItem):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        pfs_params = [
            ('x', 'X', 'The X-axis position of the tip of the root section.',
             lambda x: True, surf.origin_position.x),

            ('z', 'Z', 'The Z-axis position of the tip of the root section.',
             lambda z: True, surf.origin_position.z),

            ('height', 'Height', "The height of the vertical tail.\nHas to be positive.",
             lambda h: h > 0, surf.span),

            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.",
             lambda c: c > 0, surf.mac()),
        ]
        return pfs_params

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: Surface.template.simple_tapered(
            name=self.name,
            length=self.pfs['height'].value,
            chord=self.pfs['chord'].value,
            origin_position=(
                self.pfs['x'].value,
                0,
                self.pfs['z'].value
            ),
            airfoil=self.airfoil_chooser.airfoil,
            y_duplicate=False,
            taper_ratio=1,
            sweep_angle=0,
            inclination_angle=0,
            dihedral_angle=90,
            mid_gap=0
        )
        super()._update_surface(surface_generator)


class LMSimpleTaperedV(LeftMenuItem):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        pfs_params = [
            ('x', 'X', 'The X-axis position of the tip of the root section.',
             lambda x: True, surf.origin_position.x),

            ('z', 'Z', 'The Z-axis position of the tip of the root section.',
             lambda z: True, surf.origin_position.z),

            ('height', 'Height', "The height of the vertical tail.\nHas to be positive.",
             lambda h: h > 0, surf.span),

            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.",
             lambda c: c > 0, surf.mac()),

            ('taper', 'Taper Ratio', "The taper ratio of the surface - c_tip / c_root.\nHas to be between 0 and 1.",
             lambda tr: 0 <= tr <= 1, (surf.taper_ratio() if surf.taper_ratio() is not None else 1)),

            ('sweep', 'Sweep Angle', "Sweep angle of the wing, in degrees.\n"
                                     "The angle between Y-axis and the 25%MAC line. Positive means wing deflected backwards.\n"
                                     "Has to be between -90 and 90.",
             lambda sa: -90 < sa < 90, (surf.sweep_angle() if surf.sweep_angle() is not None else 0)),
        ]
        return pfs_params

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: Surface.template.simple_tapered(
            name=self.name,
            length=self.pfs['height'].value,
            chord=self.pfs['chord'].value,
            taper_ratio=self.pfs['taper'].value,
            sweep_angle=self.pfs['sweep'].value,
            origin_position=(
                self.pfs['x'].value,
                0,
                self.pfs['z'].value
            ),
            airfoil=self.airfoil_chooser.airfoil,
            inclination_angle=0,
            dihedral_angle=90,
            mid_gap=0,
            y_duplicate=False
        )
        super()._update_surface(surface_generator)


class LMTwinV(LeftMenuItem):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        pfs_params = [
            ('x', 'X', 'The X-axis position of the tip of the root section.',
             lambda x: True, surf.origin_position.x),

            ('z', 'Z', 'The Z-axis position of the tip of the root section.',
             lambda z: True, surf.origin_position.z),

            ('height', 'Height', "The height of the vertical tail.\nHas to be positive.",
             lambda h: h > 0, surf.span),

            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.",
             lambda c: c > 0, surf.mac()),

            ('taper', 'Taper Ratio', "The taper ratio of the surface - c_tip / c_root.\nHas to be between 0 and 1.",
             lambda tr: 0 <= tr <= 1, (surf.taper_ratio() if surf.taper_ratio() is not None else 1)),

            ('sweep', 'Sweep Angle', "Sweep angle of the wing, in degrees.\n"
                                     "The angle between Y-axis and the 25%MAC line. Positive means wing deflected backwards.\n"
                                     "Has to be between -90 and 90.",
             lambda sa: -90 < sa < 90, (surf.sweep_angle() if surf.sweep_angle() is not None else 0)),

            ('gap', 'Gap', "The gap between the two parts of the surface in meters.\n Has to be positive.",
             lambda g: g > 0, 1),
        ]
        return pfs_params

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: Surface.template.simple_tapered(
            name=self.name,
            length=self.pfs['height'].value,
            chord=self.pfs['chord'].value,
            taper_ratio=self.pfs['taper'].value,
            sweep_angle=self.pfs['sweep'].value,
            origin_position=(
                self.pfs['x'].value,
                0,
                self.pfs['z'].value
            ),
            airfoil=self.airfoil_chooser.airfoil,
            mid_gap=self.pfs['gap'].value,
            y_duplicate=True,
            inclination_angle=0,
            dihedral_angle=90
        )
        super()._update_surface(surface_generator)

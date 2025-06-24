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
from ....backend.geo_design import VerticalSurface


class LMRectangularV(LeftMenuItem):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        assert isinstance(surf, VerticalSurface)
        pfs_params = [
            ('x', 'X', 'The X-axis position of the tip of the root section.',
             lambda x: True, surf.origin_position.x),

            ('z', 'Z', 'The Z-axis position of the tip of the root section.',
             lambda z: True, surf.origin_position.z),

            ('height', 'Height', "The height of the vertical tail.\nHas to be positive.",
             lambda h: h > 0, surf.span()),

            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.",
             lambda c: c > 0, surf.mac()),
        ]
        return pfs_params

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: VerticalSurface.simple_tapered(
            name=self.name,
            height=self.pfs['height'].value,
            mac=self.pfs['chord'].value,
            origin_position=(
                self.pfs['x'].value,
                0,
                self.pfs['z'].value
            ),
            airfoil=self.airfoil_chooser.airfoil
        )
        super()._update_surface(surface_generator)

    def init_mechanization(self):
        ...


class LMSimpleTaperedV(LeftMenuItem):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        assert isinstance(surf, VerticalSurface)
        pfs_params = [
            ('x', 'X', 'The X-axis position of the tip of the root section.',
             lambda x: True, surf.origin_position.x),

            ('z', 'Z', 'The Z-axis position of the tip of the root section.',
             lambda z: True, surf.origin_position.z),

            ('height', 'Height', "The height of the vertical tail.\nHas to be positive.",
             lambda h: h > 0, surf.span()),

            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.",
             lambda c: c > 0, surf.mac()),

            ('taper', 'Taper Ratio', "The taper ratio of the surface - c_tip / c_root.\nHas to be between 0 and 1.",
             lambda tr: 0 <= tr <= 1, 1),

            ('sweep', 'Sweep Angle', "Sweep angle of the wing, in degrees.\n"
                                     "The angle between Y-axis and the 25%MAC line. Positive means wing deflected backwards.\n"
                                     "Has to be between -90 and 90.",
             lambda sa: -90 < sa < 90, 0),
        ]
        return pfs_params

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: VerticalSurface.simple_tapered(
            name=self.name,
            height=self.pfs['height'].value,
            mac=self.pfs['chord'].value,
            taper_ratio=self.pfs['taper'].value,
            sweep_angle=self.pfs['sweep'].value,
            origin_position=(
                self.pfs['x'].value,
                0,
                self.pfs['z'].value
            ),
            airfoil=self.airfoil_chooser.airfoil
        )
        super()._update_surface(surface_generator)

    def init_mechanization(self):
        ...


class LMTwinV(LeftMenuItem):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        assert isinstance(surf, VerticalSurface)
        pfs_params = [
            ('x', 'X', 'The X-axis position of the tip of the root section.',
             lambda x: True, surf.origin_position.x),

            ('z', 'Z', 'The Z-axis position of the tip of the root section.',
             lambda z: True, surf.origin_position.z),

            ('height', 'Height', "The height of the vertical tail.\nHas to be positive.",
             lambda h: h > 0, surf.span()),

            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.",
             lambda c: c > 0, surf.mac()),

            ('taper', 'Taper Ratio', "The taper ratio of the surface - c_tip / c_root.\nHas to be between 0 and 1.",
             lambda tr: 0 <= tr <= 1, 1),

            ('sweep', 'Sweep Angle', "Sweep angle of the wing, in degrees.\n"
                                     "The angle between Y-axis and the 25%MAC line. Positive means wing deflected backwards.\n"
                                     "Has to be between -90 and 90.",
             lambda sa: -90 < sa < 90, 0),

            ('gap', 'Gap', "The gap between the two parts of the surface in meters.\n Has to be positive.",
             lambda g: g > 0, surf.sections[0].y * 2),
        ]
        return pfs_params

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: VerticalSurface.simple_tapered(
            name=self.name,
            height=self.pfs['height'].value,
            mac=self.pfs['chord'].value,
            taper_ratio=self.pfs['taper'].value,
            sweep_angle=self.pfs['sweep'].value,
            origin_position=(
                self.pfs['x'].value,
                0,
                self.pfs['z'].value
            ),
            airfoil=self.airfoil_chooser.airfoil,
            gap=self.pfs['gap'].value,
        )
        super()._update_surface(surface_generator)

    def init_mechanization(self):
        ...
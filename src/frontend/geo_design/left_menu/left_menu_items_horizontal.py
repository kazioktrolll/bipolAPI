"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""
from typing import Callable, Any
from customtkinter import StringVar
from functools import cached_property

from .left_menu_item import LeftMenuItem
from ..mechanization_chooser import ControlTypeItem
from ... import FlapItem
from ....backend.geo_design import HorizontalSurface


class LMTapered(LeftMenuItem):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        assert isinstance(surf, HorizontalSurface)
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
             lambda tr: 0 <= tr <= 1, (surf.taper_ratio() if surf.taper_ratio() is not None else 1)),

            ('sweep', 'Sweep Angle', "Sweep angle of the wing, in degrees.\n"
                                     "The angle between Y-axis and the 25%MAC line. Positive means wing deflected backwards.\n"
                                     "Has to be between -90 and 90.",
             lambda sa: -90 < sa < 90, (surf.sweep_angle() if surf.sweep_angle() is not None else 0)),

            ('inclination', 'Inclination', "The inclination of the surface, in degrees\n.",
             lambda i: True, surf.sections[0].inclination)
        ]
        return pfs_params

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: HorizontalSurface.simple_tapered(
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

    def init_mechanization(self):
        assert isinstance(self.surface, HorizontalSurface)
        if not self.surface.mechanization: return
        for key, list_of_ranges in self.surface.mechanization.items():
            key = key.capitalize()
            list_preset = ControlTypeItem(key, self.update_surface, True)
            for start, stop, xc in list_of_ranges:
                item = FlapItem()
                item.set_values(StringVar(value=f'{start}'), StringVar(value=f'{stop}'), StringVar(value=f'{xc}'))
                list_preset.add_position(item)
            self.mechanizations.add_position(list_preset)


class LMRectangular(LMTapered):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        assert isinstance(surf, HorizontalSurface)
        pfs_params = [
            ('x', 'X', 'The X-axis position of the tip of the root section.',
             lambda x: True, surf.origin_position.x),

            ('z', 'Z', 'The Z-axis position of the tip of the root section.',
             lambda z: True, surf.origin_position.z),

            ('span', 'Span', "The span of the horizontal tail.\nHas to be positive.",
             lambda w: w > 0, surf.span()),

            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.",
             lambda c: c > 0, surf.mac()),

            ('inclination', 'Inclination', "The inclination of the surface, in degrees\n.",
             lambda i: True, surf.sections[0].inclination)
        ]
        return pfs_params

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: HorizontalSurface.simple_tapered(
            name=self.name,
            span=self.pfs['span'].value,
            chord_length=self.pfs['chord'].value,
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


class LMDelta(LMTapered):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        assert isinstance(surf, HorizontalSurface)
        pfs_params = [
            ('x', 'X', 'The X-axis position of the tip of the root section.',
             lambda x: True, surf.origin_position.x),

            ('z', 'Z', 'The Z-axis position of the tip of the root section.',
             lambda z: True, surf.origin_position.z),

            ('span', 'Span', "The span of the horizontal tail.\nHas to be positive.",
             lambda b: b > 0, surf.span()),

            ('surface_area', 'Surface Area', "The area of the surface.\nHas to be positive.",
             lambda s: s > 0, surf.area()),

            ('inclination', 'Inclination', "The inclination of the surface, in degrees\n.",
             lambda i: True, surf.sections[0].inclination)
        ]
        return pfs_params

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: HorizontalSurface.delta(
            name=self.name,
            span=self.pfs['span'].value,
            surface_area=self.pfs['surface_area'].value,
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

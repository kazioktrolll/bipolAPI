"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""
from typing import Callable, Any
from functools import cached_property

from .left_menu_item import LeftMenuItem
from ....backend.geo_design import Surface


class LMTapered(LeftMenuItem):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        pfs_params = [
            ('pos', 'Position XZ', 'The X and Z positions of the tip of the root section.',
             lambda tup: True, (surf.origin_position.x, surf.origin_position.z), 'Vector2'),

            ('span', 'Span', "The span of the horizontal tail.\nHas to be positive.",
             lambda w: w > 0, surf.span),

            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.",
             lambda c: c > 0, surf.mac()),

            ('taper', 'Taper Ratio', "The taper ratio of the surface - c_tip / c_root.\nHas to be between 0 and 1.",
             lambda tr: 0 <= tr <= 1, (surf.taper_ratio() if surf.taper_ratio() is not None else 1)),

            ('sweep', 'Sweep Angle', "Sweep angle of the wing, in degrees.\n"
                                     "The angle between Y-axis and the 25%MAC line. Positive means wing deflected backwards.\n"
                                     "Has to be between -90 and 90.",
             lambda sa: -90 < sa < 90, (surf.sweep_angle() if surf.sweep_angle() is not None else 0)),

            ('inclination', 'Inclination', "The inclination of the surface, in degrees\n.",
             lambda i: True, surf.sections[0].inclination),

            ('dihedral', 'Dihedral', "The dihedral of the surface, in degrees\n.",
             lambda d: -90 < d < 90, surf.sections[0].inclination)
        ]
        return pfs_params

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
            mid_gap=0,
            y_duplicate=True
        )
        do_with_surface = lambda surface: surface.set_mechanization(**self.mechanizations.get_values())
        super()._update_surface(surface_generator, do_with_surface)


class LMRectangular(LMTapered):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        pfs_params = [
            ('pos', 'Position XZ', 'The X and Z positions of the tip of the root section.',
             lambda tup: True, (surf.origin_position.x, surf.origin_position.z), 'Vector2'),

            ('span', 'Span', "The span of the horizontal tail.\nHas to be positive.",
             lambda w: w > 0, surf.span),

            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.",
             lambda c: c > 0, surf.mac()),

            ('inclination', 'Inclination', "The inclination of the surface, in degrees\n.",
             lambda i: True, surf.sections[0].inclination)
        ]
        return pfs_params

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
            y_duplicate=True,
            dihedral_angle=0
        )
        do_with_surface = lambda surface: surface.set_mechanization(**self.mechanizations.get_values())
        super()._update_surface(surface_generator, do_with_surface)


class LMDelta(LMTapered):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        pfs_params = [
            ('pos', 'Position XZ', 'The X and Z positions of the tip of the root section.',
             lambda tup: True, (surf.origin_position.x, surf.origin_position.z), 'Vector2'),

            ('span', 'Span', "The span of the horizontal tail.\nHas to be positive.",
             lambda b: b > 0, surf.span),

            ('surface_area', 'Surface Area', "The area of the surface.\nHas to be positive.",
             lambda s: s > 0, surf.area()),

            ('inclination', 'Inclination', "The inclination of the surface, in degrees\n.",
             lambda i: True, surf.sections[0].inclination)
        ]
        return pfs_params

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
        do_with_surface = lambda surface: surface.set_mechanization(**self.mechanizations.get_values())
        super()._update_surface(surface_generator, do_with_surface)


class LMDoubleTrapez(LeftMenuItem):
    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        surf = self.surface
        pfs_params = [
            ('pos', 'Position XZ', 'The X and Z positions of the tip of the root section.',
             lambda tup: True, (surf.origin_position.x, surf.origin_position.z), 'Vector2'),

            ('root_chord', 'Root Chord', "The chord of the surface at its root section.",
             lambda c: c > 0, surf.sections[0].chord),

            ('mid_chord', 'Mid Chord', "The chord of the surface at the section where it changes the geometry.",
             lambda c: c > 0, surf.mac()),#TODO fill

            ('tip_chord', 'Tip Chord', "The chord of the surface at its tip section.",
             lambda c: c > 0, surf.sections[-1].chord),

            ('mo', 'Middle Offset XYZ', '',
             lambda tup: True, (0, 1, 0), 'Vector3'), #TODO fill

            ('to', 'Tip Offset XYZ', '',
             lambda tup: True, (surf.sections[-1].leading_edge_position.tuple()), 'Vector3'),

            ('inclination', 'Inclination', "The inclination of the surface, in degrees\n.",
             lambda i: True, surf.sections[0].inclination)
        ]
        return pfs_params

    def update_surface(self, _=None) -> None:
        surface_generator = lambda: Surface.template.double_trapez(
            name=self.name,
            root_chord=self.pfs['root_chord'].value,
            mid_chord=self.pfs['mid_chord'].value,
            tip_chord=self.pfs['tip_chord'].value,
            mid_offset=self.pfs['mo'].value,
            tip_offset=self.pfs['to'].value,    # TODO ogarnąć
            origin_position=(
                self.pfs['pos'].value[0],
                0,
                self.pfs['pos'].value[1]
            ),
            inclination_angle=self.pfs['inclination'].value,
            airfoil=self.airfoil_chooser.airfoil
        )
        do_with_surface = lambda surface: surface.set_mechanization(**self.mechanizations.get_values())
        super()._update_surface(surface_generator, do_with_surface)

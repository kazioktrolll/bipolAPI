"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from pathlib import Path
from typing import TextIO

from .surface import Surface
from ..math_functions import distribute_units
from ..vector3 import Vector3, AnyVector3


class Geometry:
    """
    A class representing aircraft's geometry.

    Attributes:
        name (str): The name of the aircraft.
        mach (float): The cruise speed of the aircraft as Mach number.
        ref_pos (Vector3): The reference position of the aircraft, ideally the position of the center of mass.
        surfaces (Dict[str, Surface]): The ``Surface`` objects associated with the aircraft.
        wing (Surface|None): The wing of the aircraft. Returns 'None' if the aircraft has no defined wing.
    """

    def __init__(self,
                 name: str,
                 mach: float = 0,
                 ref_pos: AnyVector3 = Vector3.zero(),
                 surfaces: list[Surface] = None):
        """
        Parameters:
            name (str): The name of the aircraft.
            mach (float): The cruise speed of the aircraft as Mach number.
            ref_pos (AnyVector3): The reference position of the aircraft, ideally the position of the center of mass.
            surfaces (list[Surface]): The ``Surface`` objects associated with the aircraft.
        """
        self.name = name
        self.mach = mach
        self.ref_pos = Vector3(*ref_pos)
        self.surfaces = {surf.name: surf for surf in surfaces} if surfaces else {}

    def add_surface(self, surface: Surface) -> None:
        """Add a new surface. The name must be unique."""
        if surface.name in self.surfaces.keys(): raise AttributeError("A surface with name {} already exists.".format(surface.name))
        self.surfaces[surface.name] = surface

    def replace_surface(self, surface: Surface) -> None:
        """Replace an existing surface with the new surface."""
        if surface.name not in self.surfaces.keys(): raise AttributeError("No surface named {}.".format(surface.name))
        self.surfaces[surface.name] = surface

    def string(self) -> str:
        """Returns the current geometry as a .avl type string."""
        _r = (f"{self.name}\n"
              f"0.0 | Mach\n"
              f"0 0 0 | iYsym iZsym Zsym\n"
              f"{self.surface_area} {self.chord_length} {self.span_length} | Sref Cref Bref\n"
              f"{self.ref_pos.avl_string} | Xref Yref Zref\n"
              f"0.0 | CDp\n")

        for surf in self.surfaces.values():
            _r += "\n#----------------\n\n"
            _r += surf.string()

        return _r

    def save_to_avl(self, path: Path) -> TextIO:
        """Saves the current geometry to a file using .avl format."""
        contents = self.string()
        file = open(path, 'w')
        file.write(contents)
        return file

    def get_controls(self):
        """Returns the control surfaces of the aircraft in the order in which they will appear in .avl file."""
        from .section import Control
        controls: list[Control] = []
        for surf in self.surfaces.values():
            ctrls = surf.get_controls()
            controls += [c for c in ctrls if c not in controls]
        return controls

    def distribute_points(self, nof_points=500) -> None:
        """Distributes the given number of AVL calculation points over all surfaces. Must not be higher than 3000."""
        if len(self.surfaces) == 0: return
        if nof_points > 3000:
            raise AttributeError("The number of points cannot be greater than 3000.")
        min_points = [surf.min_points() for surf in self.surfaces.values()]
        areas = [surf.area() ** 0.5 for surf in self.surfaces.values()]
        distribution = distribute_units(nof_points - sum(min_points), areas)
        for surf, points in zip(self.surfaces.values(), distribution):
            surf.distribute_points(surf.min_points() + points)

    @property
    def main_surface(self) -> Surface:
        """Returns the main surface of the aircraft."""
        if 'Wing' in self.surfaces.keys():
            return self.surfaces['Wing']
        surfs = [(s, s.area()) for s in self.surfaces.values()]
        surfs.sort(key=lambda x: x[1], reverse=True)
        return surfs[0][0]

    @property
    def span_length(self):
        if len(self.surfaces) == 0: return 0
        return self.main_surface.span

    @property
    def chord_length(self):
        if len(self.surfaces) == 0: return 0
        return self.main_surface.mac()

    @property
    def surface_area(self):
        if len(self.surfaces) == 0: return 0
        return self.main_surface.area()

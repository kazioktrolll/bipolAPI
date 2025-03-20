from typing import Optional, TextIO
from pathlib import Path
from .surface import Surface
from ..vector3 import Vector3, AnyVector3


class Geometry:
    """
    A class representing aircraft's geometry.

    Attributes:
        name (str): The name of the aircraft.
        surface_area (float): The surface area of the aircraft.
        chord_length (float): The mean aerodynamic chord length of the aircraft.
        span_length (float): The wingspan of the aircraft.
        mach (float): The cruise speed of the aircraft as Mach number.
        ref_pos (Vector3): The reference position of the aircraft, ideally the position of the center of mass.
        surfaces (Dict[str, Surface]): The ``Surface`` objects associated with the aircraft.
        wing (Surface|None): The wing of the aircraft. Returns 'None' if the aircraft has no defined wing.
    """

    def __init__(self,
                 name: str,
                 chord_length: float,
                 span_length: float,
                 surface_area: float = 0,
                 mach: float = 0,
                 ref_pos: AnyVector3 = Vector3.zero(),
                 surfaces: list[Surface] = None):
        """
        Parameters:
            name (str): The name of the aircraft.
            chord_length (float): The mean aerodynamic chord length of the aircraft.
            span_length (float): The wingspan of the aircraft.
            surface_area (float): The surface area of the aircraft. If not given, will be calculated as chord*span.
            mach (float): The cruise speed of the aircraft as Mach number.
            ref_pos (AnyVector3): The reference position of the aircraft, ideally the position of the center of mass.
            surfaces (list[Surface]): The ``Surface`` objects associated with the aircraft.
        """
        self.name = name
        self.mach = mach
        self.chord_length = chord_length
        self.span_length = span_length
        self.surface_area = surface_area or chord_length * span_length
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
        _r = (f"{self.name} +  | Case Name\n"
              f"0.0 | Mach\n"
              f"0 0 0 | iYsym iZsym Zsym\n"
              f"{self.surface_area} {self.chord_length} {self.span_length} | Sref Cref Bref\n"
              f"{self.ref_pos.avl_string} | Xref Yref Zref\n"
              f"0.0 | CDp\n")

        for surf in self.surfaces.values():
            _r += "\n#----------------\n\n"
            _r += surf.string()

        return _r

    def save_to_avl(self, case_name: str, path: Path) -> TextIO:
        """Saves the current geometry to a file using .avl format."""
        contents = self.string()
        file = open(path, 'w')
        file.write(contents)
        return file

    def get_controls(self):
        from .section import Control
        controls: list[Control] = []
        for surf in self.surfaces.values():
            ctrls = surf.get_controls()
            controls += [c for c in ctrls if c not in controls]
        return controls

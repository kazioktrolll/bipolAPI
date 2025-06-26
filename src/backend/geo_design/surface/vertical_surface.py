from .surface import Surface
from ..airfoil import Airfoil
from ..section import Section
from ...vector3 import Vector3, AnyVector3
from math import tan, radians, atan, degrees
from typing import Literal


class VerticalSurface(Surface):
    """
    A class representing a single lifting surface of the aircraft, oriented vertically.

    Attributes:
        name (str): The name of the lifting surface.
        y_duplicate (bool): Whether the lifting surface should be mirrored about Y-axis.
        origin_position (Vector3): Position of the leading edge of the root chord.
        airfoil (Airfoil): The airfoil of the surface.
        sections (list[Section]): The sections of the surface. Is always sorted bottom to top.
    """

    def __init__(self,
                 name: str,
                 sections: list[Section],
                 y_duplicate: bool,
                 origin_position: AnyVector3,
                 airfoil: Airfoil = None) -> None:
        """
        Parameters:
            name (str): The name of the lifting surface.
            sections (list[Section]): Sections of the surface.
            y_duplicate (bool): Whether the lifting surface should be mirrored about Y-axis.
                Set ``True`` when defining only one half of a symmetric surface.
            origin_position (AnyVector3): Position of the leading edge of the root chord.
            airfoil (Airfoil): The airfoil of the surface.
        """
        super().__init__(name=name, sections=sections, y_duplicate=y_duplicate, origin_position=origin_position, airfoil=airfoil)

    @classmethod
    def simple_tapered(cls, name: str, height: float, mac: float,
                       origin_position: AnyVector3,
                       taper_ratio: float = 1, sweep_angle: float = 0,
                       airfoil: Airfoil = None, gap: float = 0) -> 'VerticalSurface':
        """Creates a simple tapered vertical surface.

        Parameters:
            name (str): The name of the surface.
            height (float): The height of the surface.
            mac (float): The mean aerodynamic chord of the surface.
            origin_position (AnyVector3): Position of the leading edge of the root chord.
            taper_ratio (float): The ratio the tip cord to the root chord.
            sweep_angle (float): The sweep angle of the surface.
            airfoil (Airfoil): An Airfoil object.
            gap (float): horizontal gap between the surface's halves in meters."""
        r_chord = 2 * mac / (1 + taper_ratio)
        t_chord = r_chord * taper_ratio
        tip_y = r_chord * .25 + height * tan(radians(sweep_angle)) - t_chord * 0.25
        root = Section((0, gap/2, 0), r_chord, 0)
        tip = Section((tip_y, gap/2, height), t_chord, 0)
        surf = cls(name=name, y_duplicate=(gap != 0), origin_position=origin_position, sections=[root, tip], airfoil=airfoil)
        return surf

    def get_type(self, accuracy=0.05) -> None | Literal['Rectangular', 'Simple Tapered']:
        tapered = VerticalSurface.is_simple_tapered(self, accuracy)

        if tapered and self.taper_ratio() == 1 and self.sweep_angle() == 0: return 'Rectangular'
        if tapered: return 'Simple Tapered'
        return None

    @staticmethod
    def is_simple_tapered(surface: 'VerticalSurface', accuracy=.05) -> bool:
        root = surface.sections[0]
        tip = surface.sections[-1]

        x_eq = lambda _z: root.x + ((tip.x - root.x) / (tip.z - root.z)) * _z
        c_eq = lambda _z: root.chord + ((tip.chord - root.chord) / (tip.z - root.y)) * _z

        # Check if the surface is of correct shape
        for section in surface.sections:
            if section is root or section is tip: continue
            z = section.z
            x = section.leading_edge_position.x
            c = section.chord
            x_exp = x_eq(z)
            c_exp = c_eq(z)
            if abs(x_exp - x) > accuracy: return False
            if abs(c_exp - c) > accuracy: return False
        return True

    def taper_ratio(self) -> float:
        if not VerticalSurface.is_simple_tapered(self, 0.05):
            raise ValueError('Surface is too complex')
        return self.sections[-1].chord / self.sections[0].chord

    def sweep_angle(self) -> float:
        if not VerticalSurface.is_simple_tapered(self, 0.05):
            raise ValueError('Surface is too complex')
        root = self.sections[0].get_position_at_xc(.25)
        tip = self.sections[-1].get_position_at_xc(.25)
        sweep = degrees(atan((tip.x - root.x) / (tip.z - root.z)))
        return sweep

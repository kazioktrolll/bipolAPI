from .surface import Surface
from ..airfoil import Airfoil
from ..section import Section
from ...vector3 import Vector3, AnyVector3
from math import tan, radians
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

    def get_type(self, accuracy=0.05) -> None | Literal['Rectangular', 'Simple Tapered']:
        tapered = VerticalSurface.is_simple_tapered(self, accuracy)

        if tapered and self.taper_ratio() == 1 and self.sweep_angle() == 0: return 'Rectangular'
        if tapered: return 'Simple Tapered'
        return None

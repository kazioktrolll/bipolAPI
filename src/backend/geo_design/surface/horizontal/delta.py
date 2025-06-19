from .horizontal_simple_surface import HorizontalSimpleSurface
from ...airfoil import Airfoil
from ....vector3 import Vector3, AnyVector3
from math import degrees, atan


class DeltaSurface(HorizontalSimpleSurface):
    def __init__(self,
                 name: str,
                 span: float,
                 surface_area: float,
                 origin_position: AnyVector3 = Vector3.zero(),
                 inclination_angle: float = 0.0,
                 airfoil: Airfoil = None):
        """

        :param name: Name of the surface.
        :param span: Span of the surface in meters.
        :param surface_area: Surface area of the surface in meters squared.
        :param origin_position: Origin position of the surface in meters.
        :param inclination_angle: Inclination angle of the surface in degrees.
        :param airfoil: Airfoil object.
        """

        chord = surface_area / span
        sweep = degrees(atan(3/2 * chord / span))
        super().__init__(name=name, span=span, origin_position=origin_position, airfoil=airfoil,
                         inclination_angle=inclination_angle, taper_ratio=0, chord_length=chord,
                         sweep_angle=sweep)

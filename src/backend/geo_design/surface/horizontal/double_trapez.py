from .horizontal_surface import HorizontalSurface
from ...section import Section
from ...airfoil import Airfoil
from ....vector3 import Vector3, AnyVector3


class DoubleTrapezSurface(HorizontalSurface):
    def __init__(self,
                 name: str,
                 root_chord: float,
                 mid_chord: float,
                 tip_chord: float,
                 mid_offset: AnyVector3,
                 tip_offset: AnyVector3,
                 origin_position: AnyVector3 = Vector3.zero(),
                 inclination_angle: float = 0,
                 airfoil: Airfoil = None):
        root = Section(
            leading_edge_position=(0, 0, 0),
            chord=root_chord,
            inclination=inclination_angle,
            airfoil=airfoil
        )
        mid = Section(
            leading_edge_position=mid_offset,
            chord=mid_chord,
            inclination=inclination_angle,
            airfoil=airfoil
        )
        tip = Section(
            leading_edge_position=tip_offset,
            chord=tip_chord,
            inclination=inclination_angle,
            airfoil=airfoil
        )

        super().__init__(name=name, y_duplicate=True, origin_position=origin_position, airfoil=airfoil, sections=[root, mid, tip])

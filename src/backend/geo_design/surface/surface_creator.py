from .horizontal import HorizontalSurface
from .vertical_simple_surface import VerticalSimpleSurface
from ..airfoil import Airfoil
from ..section import Section
from ...vector3 import AnyVector3


class SurfaceCreator:
    @classmethod
    def UnknownSurface(cls,
                       name: str,
                       sections: list[Section],
                       y_duplicate: bool,
                       origin_position: AnyVector3,
                       airfoil: Airfoil = None
                       ) -> HorizontalSurface | VerticalSimpleSurface:
        """Returns a HorizontalSurface or VerticalSurface based on input geometry."""
        sections.sort(key=lambda section: section.y)
        dy = sections[-1].y - sections[0].y
        sections.sort(key=lambda section: section.z)
        dz = sections[-1].z - sections[0].z
        """Decides which Surface class is appropriate based on input parameters,
        creates and returns an instance accordingly."""
        if dy >= dz:
            return HorizontalSurface(name=name, sections=sections,
                                     y_duplicate=y_duplicate, origin_position=origin_position, airfoil=airfoil)
        else:
            return VerticalSimpleSurface(name=name, sections=sections,
                                         y_duplicate=y_duplicate, origin_position=origin_position, airfoil=airfoil)

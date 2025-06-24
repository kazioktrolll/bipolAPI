from .surface import Surface
from ..airfoil import Airfoil
from ..section import Section
from ...vector3 import Vector3, AnyVector3
from math import tan, radians


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

    def major_axis(self, section: Section) -> float:
        return section.z

    def minor_axis(self, section: Section) -> float:
        return section.y

    def xmamina_to_xyz(self, x: float, ma: float, mina: float) -> Vector3:
        return Vector3(x, mina, ma)

    def span(self) -> float:
        span = self.sections[-1].z - self.sections[0].z
        return span

    def add_section_gentle(self, z: float | list[float]) -> None:
        super().add_section_gentle(ma=z)

    def has_section_at(self, z: float) -> bool:
        """Returns ``True`` if the surface has a section at given ``z``."""
        return super().has_section_at(ma=z)

    def get_section_at(self, z: float) -> Section | None:
        """Returns the section at given ``z``, if exists, else returns ``None``."""
        return super().get_section_at(ma=z)

    def get_sections_between(self, z_start: float, z_end: float,
                             include_start: bool = True, include_end: bool = False) -> list[Section]:
        """Returns a list of sections between ``z_start`` and ``z_end``."""
        return super().get_sections_between(ma_start=z_start, ma_end=z_end,
                                            include_start=include_start, include_end=include_end)

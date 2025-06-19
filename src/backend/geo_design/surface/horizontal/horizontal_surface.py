from ..surface import Surface
from ...section import Section
from ...airfoil import Airfoil
from ....vector3 import Vector3, AnyVector3


class HorizontalSurface(Surface):
    """
    A class representing a single lifting surface of the aircraft, oriented more-or-less horizontally.

    Attributes:
        name (str): The name of the lifting surface.
        y_duplicate (bool): Whether the lifting surface should be mirrored about Y-axis.
        origin_position (Vector3): Position of the leading edge of the root chord.
        airfoil (Airfoil): The airfoil of the surface.
        sections (list[Section]): The sections of the surface. Is always sorted left wingtip-to-right wingtip.
        """

    def __init__(self,
                 name: str,
                 sections: list[Section],
                 y_duplicate: bool,
                 origin_position: AnyVector3,
                 airfoil: Airfoil = None):
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

    def major_axis(self, section: Section) -> float:
        return section.y

    def minor_axis(self, section: Section) -> float:
        return section.z

    def xmamina_to_xyz(self, x: float, ma: float, mina: float) -> Vector3:
        return Vector3(x, ma, mina)

    def span(self) -> float:
        span = self.sections[-1].y - self.sections[0].y
        if self.y_duplicate: span *= 2
        return span

    def add_section_gentle(self, y: float | list[float]) -> None:
        super().add_section_gentle(ma=y)

    def has_section_at(self, y: float) -> bool:
        """Returns ``True`` if the surface has a section at given ``y``."""
        return super().has_section_at(ma=y)

    def get_section_at(self, y: float) -> Section | None:
        """Returns the section at given ``y``, if exists, else returns ``None``."""
        return super().get_section_at(ma=y)

    def get_sections_between(self, y_start: float, y_end: float,
                             include_start: bool = True, include_end: bool = False) -> list[Section]:
        """Returns a list of sections between ``y_start`` and ``y_end``."""
        return super().get_sections_between(ma_start=y_start, ma_end=y_end,
                                            include_start=include_start, include_end=include_end)

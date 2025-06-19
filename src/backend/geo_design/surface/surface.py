"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from ..section import Section, Control
from ..airfoil import Airfoil
from ...to_re_docstring_decorator import to_re_docstring
from ...vector3 import Vector3, AnyVector3
from ...math_functions import best_factor_pair, distribute_units
from abc import ABC, abstractmethod


class Surface(ABC):
    """
    An abstract class representing a single lifting surface of the aircraft.

    Attributes:
        name (str): The name of the lifting surface.
        y_duplicate (bool): Whether the lifting surface should be mirrored about Y-axis.
        origin_position (Vector3): Position of the leading edge of the root chord.
        airfoil (Airfoil): The airfoil of the surface.
        sections (list[Section]): The sections of the surface.
          Is always sorted along the surface's major axis, ascending.
    """

    @to_re_docstring
    def __init__(self,
                 name: str,
                 sections: list[Section],
                 y_duplicate: bool,
                 origin_position: AnyVector3,
                 airfoil: Airfoil = None, ):
        """
        Parameters:
            name (str): The name of the lifting surface.
                If named 'Wing', 'H_tail', 'V_tail' - will be recognized as such by the ``Geometry`` instance.
                It is not used for geometry generation, just for calculations.
            sections (list[Section]): Sections of the surface.
            y_duplicate (bool): Whether the lifting surface should be mirrored about Y-axis.
                Set ``True`` when defining only one half of a symmetric surface.
            origin_position (AnyVector3): Position of the leading edge of the root chord.
            airfoil (Airfoil): The airfoil of the surface.
        """
        self.name = name
        self.y_duplicate = y_duplicate
        self.origin_position = Vector3(*origin_position)
        self.airfoil = airfoil if airfoil else Airfoil.empty()
        if not len(sections) >= 2: raise ValueError("Cannot create a surface with less than two sections.")
        self.sections = sections
        self.sort_sections()
        self.chord_points = 1

    def __repr__(self) -> str:
        return self.name

    @abstractmethod
    def major_axis(self, section: Section) -> float:
        """Returns the position of the section along the major axis of the surface."""

    @abstractmethod
    def minor_axis(self, section: Section) -> float:
        """Returns the position of the section along the minor axis of the surface."""

    @abstractmethod
    def xmamina_to_xyz(self, x: float, ma: float, mina: float) -> Vector3:
        """
        Transforms coordinates from xmamina base to xyz base.

        Parameters:
            x (float): The x position of the section.
            ma (float): The major axis position of the section.
            mina (float): The minor axis position of the section.
        """

    @abstractmethod
    def span(self) -> float:
        """Returns the span of the surface."""

    def area(self) -> float:
        """Returns the area of the surface."""
        # For each section, A = 1/2 * ||(B-A)x(C-A)|| + 1/2 * ||(C-A)x(D-A)||
        # Where ABCD are tips of the section: A=prev.le, B=prev.te, C=next.te, D=next.le
        area = 0
        for i in range(len(self.sections) - 1):
            prev = self.sections[i]
            next = self.sections[i + 1]
            A = prev.leading_edge_position
            B = A + (prev.chord, 0, 0)
            D = next.leading_edge_position
            C = D + (next.chord, 0, 0)
            sect_area = 0.5 * ((B-A).cross_product(C-A)).length() + 0.5 * ((C-A).cross_product(D-A)).length()
            area += sect_area
        return area

    def mac(self) -> float:
        return self.area() / self.span()

    def sort_sections(self) -> None:
        """Sorts the sections along the major axis of the surface."""
        self.sections.sort(key=lambda section: self.major_axis(section))

    def add_section(self, section: Section) -> None:
        """Add a new section to the surface and ensures the sections are well-ordered."""
        # Check whether the section is not outside the wing.
        if not self.major_axis(self.sections[0]) < self.major_axis(section) < self.major_axis(self.sections[-1]): return
        # Check if a section with identical major axis coordinate doesn't already exist.
        if self.major_axis(section) in [self.major_axis(sec) for sec in self.sections]: return

        self.sections.append(section)
        self.sort_sections()

    @to_re_docstring
    def add_section_gentle(self, ma: float | list[float]) -> None:
        """Add a new section to the surface without modifying the shape of the surface."""
        if isinstance(ma, list):
            for ma_i in ma:
                self.add_section_gentle(ma_i)
            return

        assert isinstance(ma, (int, float))

        for i, sec in enumerate(self.sections):
            if self.major_axis(sec) >= ma:
                prev_sec = self.sections[i - 1]
                next_sec = sec
                break
        else:
            raise Exception('Incorrect major axis coordinate!')

        # Calculate leading edge position as prev.x + dma * dx
        dma = (ma - self.major_axis(prev_sec)) / (self.major_axis(next_sec) - self.major_axis(prev_sec))
        xle = (prev_sec.leading_edge_position.x + dma *
               (next_sec.leading_edge_position.x - prev_sec.leading_edge_position.x))
        mina = self.minor_axis(prev_sec) + dma * (self.minor_axis(next_sec) - self.minor_axis(prev_sec))
        chord = prev_sec.chord + dma * (next_sec.chord - prev_sec.chord)
        inc = prev_sec.inclination + dma * (next_sec.inclination - prev_sec.inclination)
        sec = Section(self.xmamina_to_xyz(xle, ma, mina), chord, inc, self.airfoil)
        self.add_section(sec)

    def get_symmetric(self) -> 'Surface':
        """Returns a copy of the surface mirrored about Y-axis."""
        from copy import copy
        surf = copy(self)
        surf.name = self.name + '_symm'  # noqa
        reflected_sections = [sec.mirror() for sec in self.sections]
        surf.sections = reflected_sections
        return surf

    @to_re_docstring
    def has_section_at(self, ma: float) -> bool:
        """Returns ``True`` if the surface has a section at given major axis coordinate."""
        mas = [self.major_axis(section) for section in self.sections]
        return ma in mas

    @to_re_docstring
    def get_section_at(self, ma: float) -> Section | None:
        """Returns the section at given major axis coordinate, if exists, else returns ``None``."""
        if not self.has_section_at(ma): return None
        for sec in self.sections:
            if self.major_axis(sec) == ma:
                return sec

    @to_re_docstring
    def get_sections_between(self, ma_start: float, ma_end: float,
                             include_start: bool = True, include_end: bool = False
                             ) -> list[Section]:
        """Returns a list of sections between ``ma_start`` and ``ma_end``."""
        if not ma_start < ma_end:
            raise Exception('ma_start must be smaller than ma_end!')
        secs = []
        if include_start and self.has_section_at(ma_start):
            secs.append(self.get_section_at(ma_start))

        secs += [section for section in self.sections if ma_start < self.major_axis(section) < ma_end]

        if include_end and self.has_section_at(ma_end):
            secs.append(self.get_section_at(ma_end))

        return secs

    def min_points(self) -> int:
        """Returns the minimal number of vortex points required for this surface. """
        return len(self.sections) - 1

    def distribute_points(self, nof_points: int) -> None:
        chord_points, span_points = best_factor_pair(nof_points)
        self.chord_points = chord_points
        span_points -= len(self.sections) - 1 # Each section requires at least a point, except for the last one.
        lengths = []
        for i in range(len(self.sections) - 1):
            prev = self.sections[i]
            next = self.sections[i + 1]
            lengths.append((self.major_axis(prev) - self.major_axis(next)))

        spanwise_distribution = distribute_units(span_points, lengths)
        spanwise_distribution.append(-1) # For the last section, with the later '+1' will give 0
        for section, distribution in zip(self.sections, spanwise_distribution):
            section.spanwise_points = distribution + 1

    def string(self) -> str:
        """Returns the current geometry as a .avl type string."""
        _r = (f"SURFACE\n"
              f"{self.name}\n"
              f"{self.chord_points} 1.0\n" # Spanwise points are distributed per section.
              f"{'YDUPLICATE\n0.0' if self.y_duplicate else ''}\n"
              f"SCALE\n"
              f"1.0 1.0 1.0\n"
              f"TRANSLATE\n"
              f"{self.origin_position.avl_string}\n"
              f"ANGLE\n"
              f"0\n")
        for sec in self.sections:
            _r += sec.string()
        return _r

    def get_controls(self) -> list[Control]:
        """Returns the control surfaces of the surface in the order in which they will appear in the .avl file."""
        controls = []
        for sec in self.sections:
            if sec.control and sec.control not in controls:
                controls.append(sec.control)
        return controls

    def clear_controls(self) -> None:
        """Removes all control surfaces from the surface."""
        for sec in self.sections:
            sec.control = None

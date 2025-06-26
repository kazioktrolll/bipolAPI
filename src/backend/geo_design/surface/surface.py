"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from math import atan2, degrees, sqrt, radians, sin, cos
from copy import copy

from ..airfoil import Airfoil
from ..section import Section, Control, control_types
from ...math_functions import best_factor_pair, distribute_units
from ...vector3 import Vector3, AnyVector3


class Surface:
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
        self.disabled = False
        self.mechanization = {}

    def __repr__(self) -> str:
        return self.name

    @property
    def root(self) -> Section:
        return self.sections[0]

    @property
    def tip(self) -> Section:
        return self.sections[-1]

    @property
    def is_straight(self, tol = 0.05) -> bool:
        """Returns ``True`` if the surface is a straight line, as seen from the front."""
        if len(self.sections) < 2:
            return False

        if len(self.sections) == 2:
            return True

        _, yr, zr = self.root.leading_edge_position.tuple()
        _, yt, zt = self.tip.leading_edge_position.tuple()

        for section in self.sections[1:-1]:
            _, y, z = section.leading_edge_position.tuple()
            lhs = (y - yr) * (zt - zr)
            rhs = (z - zr) * (yt - yr)
            if abs(lhs - rhs) > tol:
                return False
        return True

    @property
    def dihedral(self) -> float | None:
        """Returns the dihedral angle of the surface if it is straight, else returns ``None``."""
        if not self.is_straight:
            return None
        return degrees(atan2(self.tip.z - self.root.z, self.tip.y - self.root.y))

    @property
    def span(self) -> float | None:
        """Returns the span (distance from root to tip in YZ plane) of the surface if it is straight, else returns ``None``."""
        if not self.is_straight:
            return None
        if self.y_duplicate:
            return 2 * self.spanwise(self.tip)
        return sqrt((self.tip.y - self.root.y) ** 2 + (self.tip.z - self.root.z) ** 2)

    def area(self) -> float:
        """Returns the area of the surface."""
        # For each section, A = 1/2 * ||(B-A)x(C-A)|| + 1/2 * ||(C-A)x(D-A)||
        # Where ABCD are tips of the section: A=prev.le, B=prev.te, C=next.te, D=next.le
        area = 0
        for i in range(len(self.sections) - 1):
            _prev = self.sections[i]
            _next = self.sections[i + 1]
            A = _prev.leading_edge_position
            B = A + (_prev.chord, 0, 0)
            D = _next.leading_edge_position
            C = D + (_next.chord, 0, 0)
            sect_area = 0.5 * ((B - A).cross_product(C - A)).length() + 0.5 * ((C - A).cross_product(D - A)).length()
            area += sect_area
        if self.y_duplicate:
            area *= 2
        return area

    def mac(self) -> float:
        return self.area() / self.span

    @property
    def length_yz(self) -> float:
        """Returns the length of the surface in YZ plane."""
        if len(self.sections) < 2:
            return 0
        l = 0
        for i in range(len(self.sections) - 1):
            _prev = self.sections[i]
            _next = self.sections[i + 1]
            l += sqrt((_next.y - _prev.y) ** 2 + (_next.z - _prev.z) ** 2)
        return l

    @property
    def length_abs(self) -> float:
        """Returns the absolute total length of the surface sections."""
        if len(self.sections) < 2:
            return 0
        l = 0
        for i in range(len(self.sections) - 1):
            _prev = self.sections[i].leading_edge_position
            _next = self.sections[i + 1].leading_edge_position
            l += (_next - _prev).length()
        return l

    def spanwise(self, section: Section) -> float:
        """Returns the spanwise position of the section on the surface."""
        return sqrt((section.y - self.root.y) ** 2 + (section.z - self.root.z) ** 2)

    def add_section(self, section: Section) -> None:
        """Add a new section to the surface and ensures the sections are well-ordered."""
        # Check whether the section is not outside the wing.
        if not self.spanwise(self.root) < self.spanwise(section) < self.spanwise(self.tip): return
        # Check if a section with identical major axis coordinate doesn't already exist.
        if self.spanwise(section) in [self.spanwise(sec) for sec in self.sections]: return

        self.sections.append(section)
        self.sort_sections()

    def add_section_gentle(self, spanwise: float | list[float]) -> None:
        """Add a new section to the surface without modifying the shape of the surface."""
        if isinstance(spanwise, list):
            for spn_i in spanwise:
                self.add_section_gentle(spn_i)
            return

        assert isinstance(spanwise, (int, float))

        for i, sec in enumerate(self.sections):
            if self.spanwise(sec) >= spanwise:
                prev_sec = self.sections[i - 1]
                next_sec = sec
                break
        else:
            raise Exception('Incorrect spanwise coordinate!')

        # Calculate leading edge position as prev.x + d_spanwise * dx
        d_spanwise = (spanwise - self.spanwise(prev_sec)) / (self.spanwise(next_sec) - self.spanwise(prev_sec))
        xle = (prev_sec.x + d_spanwise * (next_sec.x - prev_sec.x))
        chord = prev_sec.chord + d_spanwise * (next_sec.chord - prev_sec.chord)
        inc = prev_sec.inclination + d_spanwise * (next_sec.inclination - prev_sec.inclination)
        sec = Section(self.xspan_to_xyz(xle, spanwise), chord, inc, self.airfoil)
        self.add_section(sec)

    def sort_sections(self) -> None:
        """Sorts the sections along the major axis of the surface."""
        if len(self.sections) < 2: return
        ref_sec = self.sections[0]
        def pos(section):
            return sqrt((section.y - ref_sec.y) ** 2 + (section.z - ref_sec.z) ** 2)
        self.sections.sort(key=lambda section: pos(section))

    def get_symmetric(self) -> 'Surface2':
        """Returns a copy of the surface mirrored about Y-axis."""
        surf = copy(self)
        surf.name = self.name + '_symm'
        reflected_sections = [sec.mirror() for sec in self.sections]
        surf.sections = reflected_sections
        surf.clear_controls()
        surf.mechanization = {}
        sym_controls = {}
        for k, list_of_ranges in self.mechanization.items():
            sym_controls[k] = [(-e, -s, xc) for s, e, xc in list_of_ranges]
        surf.set_mechanization(**sym_controls)
        return surf

    def assert_straight(self):
        if not self.is_straight:
            raise Exception('Surface is not straight!')

    def has_section_at(self, spanwise: float) -> bool:
        """Returns ``True`` if the surface has a section at a given spanwise coordinate."""
        self.assert_straight()
        poss = [self.spanwise(section) for section in self.sections]
        return spanwise in poss

    def get_section_at(self, spanwise: float) -> Section | None:
        """Returns the section at a given major axis coordinate, if exists, else returns ``None``."""
        self.assert_straight()
        for sec in self.sections:
            if self.spanwise(sec) == spanwise:
                return sec
        return None

    def get_sections_between(self, spanwise_start: float, spanwise_end: float,
                             include_start: bool = True, include_end: bool = False
                             ) -> list[Section]:
        """Returns a list of sections between ``spanwise_start`` and ``spanwise_end``."""
        self.assert_straight()
        if not spanwise_start < spanwise_end:
            raise Exception('spanwise_start must be smaller than spanwise_end!')
        secs = []
        if include_start and self.has_section_at(spanwise_start):
            secs.append(self.get_section_at(spanwise_start))

        secs += [section for section in self.sections if spanwise_start < self.spanwise(section) < spanwise_end]

        if include_end and self.has_section_at(spanwise_end):
            secs.append(self.get_section_at(spanwise_end))

        return secs

    def xspan_to_xyz(self, x: float, ma: float) -> Vector3:
        y = ma * cos(radians(self.dihedral))
        z = ma * sin(radians(self.dihedral))
        return Vector3(x, y, z)

    # Nowe
    def set_mechanization(self, **kwargs: list[tuple[float, float, float]]) -> None:
        """Sets the mechanization of the surface.

        Parameters:
            **kwargs (list[tuple[float, float, float]]): For each type of control a tuple (y_start, y_stop, x_hinge).

        Usage:
            surface_instance.set_mechanization(ailerons=[(1, 2, .7), (3, 3.5, .6)], flaps=[(2.1, 2.9, .6)])

            This will create **ailerons** for ``y`` = <1 : 2> ``hinge`` 0.7 x/c and ``y`` = <3 : 3.5> ``hinge`` 0.6 x/c,
            and **flaps** for ``y`` = <2.1 : 2.9> ``hinge`` 0.6 x/c.
        """
        self.assert_straight()
        if self.mechanization:
            raise ValueError(f"The surface {self.name} already has mechanization!")
        self.mechanization = kwargs

        for key, value in kwargs.items():
            key = key.lower()
            for mech_type in control_types:
                if mech_type.is_alias(key):
                    break
            else:
                raise ValueError(f"Unknown mechanism type: {key}")
            # To add a control surface in AVL, you add a control surface to a section,
            # and it is valid up to the next section.
            for start, end, hinge_x in value:
                # Ensure there is a ``Section`` at 'span' == 'start' and 'end'.
                if not self.has_section_at(start): self.add_section_gentle(start)
                if not self.has_section_at(end): self.add_section_gentle(end)
                # Add ``Control`` to every Section between 'start' and 'end'.
                sections = self.get_sections_between(start, end, include_end=True)
                control_instance = mech_type(x_hinge=hinge_x)
                for section in sections:
                    if section.has_control: raise Exception("A section already has a control surface!")
                    section.control = control_instance

            # Check if there are blocks with the same control next to each other,
            # and if so, add a section in between.
            for i, section in enumerate(self.sections):
                if i == 0: continue
                prev_section = self.sections[i - 1]
                if section.control is None: continue
                if section.control.is_equal_to(prev_section.control) and section.control is not prev_section.control:
                    self.add_section_gentle(prev_section.y + 0.01)


    def min_points(self) -> int:
        """Returns the minimal number of vortex points required for this surface. """
        return len(self.sections) - 1

    def distribute_points(self, nof_points: int) -> None:
        chord_points, span_points = best_factor_pair(nof_points)
        self.chord_points = chord_points
        span_points -= len(self.sections) - 1  # Each section requires at least a point, except for the last one.
        lengths = []
        for i in range(len(self.sections) - 1):
            _prev = self.sections[i]
            _next = self.sections[i + 1]
            lengths.append((self.spanwise(_prev) - self.spanwise(_next)))

        spanwise_distribution = distribute_units(span_points, lengths)
        spanwise_distribution.append(-1)  # For the last section, with the later '+1' will give 0
        for section, distribution in zip(self.sections, spanwise_distribution):
            section.spanwise_points = distribution + 1

    def string(self) -> str:
        """Returns the current geometry as an .avl type string."""
        _r = (f"SURFACE\n"
              f"{self.name}\n"
              f"{self.chord_points} 1.0\n"  # Spanwise points are distributed per section.
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

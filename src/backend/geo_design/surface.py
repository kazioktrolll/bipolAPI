"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from math import atan2, degrees, sqrt, radians, sin, cos, tan
from copy import copy
from typing import Literal, Optional

from .airfoil import Airfoil
from .section import Section, Control, control_types
from ..math_functions import best_factor_pair, distribute_units
from ..vector3 import Vector3, AnyVector3


class SurfaceTemplates:
    """A factory class for ``Surface`` templates."""
    types = Literal['Rectangular', 'Delta', 'Simple Tapered', 'Double Trapez', 'Vertical Rectangular', 'Vertical Tapered']
    @staticmethod
    def simple_tapered(name: str,
                       length: float,
                       chord: float,
                       taper_ratio: float,
                       sweep_angle: float,
                       origin_position: AnyVector3,
                       inclination_angle: float,
                       dihedral_angle: float,
                       airfoil,
                       mid_gap: float
                       ) -> 'Surface':
        """
        Creates a ``Surface`` based on parameters of a simple tapered wing.

        Parameters:
            name (str): The name of the lifting surface.
            length (float): The YZ distance from root to tip.
            chord (float): The mean aerodynamic chord length of the surface.
            origin_position (AnyVector3): Position of the leading edge of the root chord.
            inclination_angle (float): The inclination of the surface, in degrees.
              Zero means horizontal, positive means leading edge up.
            airfoil (Airfoil): The airfoil of the surface.
            taper_ratio (float): The taper ratio of the surface.
            sweep_angle (float): The sweep angle of the surface in degrees.
            dihedral_angle (float): Dihedral angle of the surface, positive means tips up.
            mid_gap (float): The horizontal gap between the surface's halves' root sections in meters.
        """

        # Calculate the position and chord for both root and tip sections.

        root_chord = 2 * chord / (1 + taper_ratio)
        c_eq = lambda s: root_chord * (1 - (1 - taper_ratio) * s / length)
        mac025 = lambda s: root_chord * .25 + s * tan(radians(sweep_angle))
        le_x_eq = lambda s: mac025(s) - c_eq(s) * .25
        le_y_eq = lambda s: s * cos(radians(dihedral_angle))
        le_z_eq = lambda s: s * sin(radians(dihedral_angle))

        root = Section((0, mid_gap / 2, 0),
                       c_eq(0), inclination_angle, airfoil)
        tip = Section((le_x_eq(length), le_y_eq(length) + mid_gap / 2, le_z_eq(length)),
                      c_eq(length), inclination_angle, airfoil)

        surf = Surface(name=name,
                       sections=[root, tip],
                       origin_position=origin_position,
                       airfoil=airfoil)
        return surf

    @staticmethod
    def delta(name: str, span: float, surface_area: float,
              origin_position: AnyVector3 = Vector3.zero(),
              inclination_angle: float = 0.0,
              airfoil: Airfoil = None) -> 'Surface':
        """
        Creates a ``Surface`` based on parameters of a delta wing.

        :param name: Name of the surface.
        :param span: Span of the whole surface in meters.
        :param surface_area: Surface area of the whole surface in meters squared.
        :param origin_position: Origin position of the surface in meters.
        :param inclination_angle: Inclination angle of the surface in degrees.
        :param airfoil: Airfoil object.
        """
        chord = surface_area / span
        sweep = degrees(atan2(3 * chord, span))
        surf = SurfaceTemplates.simple_tapered(
            name=name, length=span/2, origin_position=origin_position,
            airfoil=airfoil, inclination_angle=inclination_angle,
            taper_ratio=0, chord=chord, sweep_angle=sweep, dihedral_angle=0,
            mid_gap=0
        )
        return surf

    @staticmethod
    def double_trapez(name: str,
                      root_chord: float, mid_chord: float, tip_chord: float,
                      length: float, seam_spanwise: float, origin_position: AnyVector3,
                      inclination_angle: float, airfoil: Airfoil, dihedral_angle: float, sweep_angle: float,
                      mid_gap: float) -> 'Surface':
        """
        Creates a ``Surface`` based on parameters of a double trapezoidal wing.

        :param name: Name of the surface.
        :param root_chord: Aerodynamic root chord of the surface in meters.
        :param mid_chord: Aerodynamic mid-chord of the surface in meters.
        :param tip_chord: Aerodynamic tip chord of the surface in meters.
        :param length: Span of the surface in meters.
        :param seam_spanwise: Spanwise position of the seam in meters.
        :param origin_position: Position of the root-chord-le of the surface in meters.
        :param inclination_angle: Inclination angle of the surface in degrees.
        :param airfoil: Airfoil object.
        :param dihedral_angle: Dihedral angle of the surface in degrees.
        :param sweep_angle: Sweep angle of the surface in degrees.
        :param mid_gap: Mid-gap of the surface in meters.
        """
        mac_0 = (root_chord + tip_chord) / 2
        surf = SurfaceTemplates.simple_tapered(
            name=name, length=length, origin_position=origin_position, sweep_angle=sweep_angle, dihedral_angle=dihedral_angle, airfoil=airfoil,
            inclination_angle=inclination_angle, taper_ratio=tip_chord/root_chord, chord=mac_0, mid_gap=mid_gap)

        mid_section = surf.add_section_gentle(seam_spanwise)
        mid_section.chord = mid_chord

        return surf

    @staticmethod
    def is_simple_tapered(surface: 'Surface', accuracy=.05) -> bool:
        try:
            surface.assert_straight()
        except AssertionError:
            return False
        safe_tip_y = surface.tip.y if surface.tip.y != 0 else 1e-10
        x_eq = lambda _y: surface.root.x + _y / safe_tip_y * (surface.tip.x - surface.root.x)
        z_eq = lambda _y: surface.root.z + _y / safe_tip_y * (surface.tip.z - surface.root.z)
        c_eq = lambda _y: surface.root.chord + _y / safe_tip_y * (surface.tip.chord - surface.root.chord)
        inc = surface.root.inclination

        # Check if the surface is of correct shape
        for section in surface.sections:
            if section is surface.root or section is surface.tip: continue
            y = section.y
            le = section.leading_edge_position
            c = section.chord
            if abs((le.x - x_eq(y)) / c) > accuracy: return False
            if abs((le.z - z_eq(y)) / c) > accuracy: return False
            if abs((c - c_eq(y)) / c) > accuracy: return False
            if section.inclination != inc: return False
        return True


    @staticmethod
    def is_delta(surface: 'Surface', accuracy=.05) -> bool:
        if not SurfaceTemplates.is_simple_tapered(surface, accuracy):
            return False
        root = surface.sections[0]
        tip = surface.sections[-1]
        if tip.chord != 0: return False
        if not tip.trailing_edge_position == root.trailing_edge_position: return False
        return True

    @staticmethod
    def is_double_trapez(surface: 'Surface', accuracy=.05) -> bool:
        raise NotImplementedError

    @staticmethod
    def is_vertical(surface: 'Surface', accuracy=.5) -> bool:
        if not surface.is_straight: return False
        if surface.dihedral < 90 - accuracy: return False
        return True

    @staticmethod
    def get_type(surface: 'Surface', accuracy=0.05) -> Optional['SurfaceTemplates.types']:
        vertical = SurfaceTemplates.is_vertical(surface, accuracy)
        if SurfaceTemplates.is_delta(surface, accuracy):
            return 'Delta'
        tapered = SurfaceTemplates.is_simple_tapered(surface, accuracy)
        # double_trapez = SurfaceTemplates.is_double_trapez(surface, accuracy)
        double_trapez = False
        rect = tapered and surface.taper_ratio() == 1 and surface.sweep_angle() == 0

        if vertical and rect: return 'Vertical Rectangular'
        if vertical and tapered: return 'Vertical Tapered'

        if rect: return 'Rectangular'
        if tapered: return 'Simple Tapered'
        if double_trapez: return 'Double Trapez'
        return None


class Surface:
    template = SurfaceTemplates

    def __init__(self,
                 name: str,
                 sections: list[Section],
                 origin_position: AnyVector3,
                 airfoil: Airfoil = None, ):
        """
                Parameters:
                    name (str): The name of the lifting surface.
                        If named 'Wing', 'H_tail', 'V_tail' - will be recognized as such by the ``Geometry`` instance.
                        It is not used for geometry generation, just for calculations.
                    sections (list[Section]): Sections of the surface.
                    origin_position (AnyVector3): Position of the leading edge of the root chord.
                    airfoil (Airfoil): The airfoil of the surface.
                """
        self.name = name
        self.origin_position = Vector3(*origin_position)
        self.airfoil = airfoil if airfoil else Airfoil.empty()
        if len(sections) < 2: raise ValueError("Cannot create a surface with less than two sections.")
        self.sections = sections
        self.sort_sections()
        self.chord_points = 1
        self.disabled = False
        self._lock_y_duplicate: None | bool = None
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
    def y_duplicate(self) -> bool:
        """Returns ``True`` if the surface should be mirrored about Y-axis."""
        if self._lock_y_duplicate is not None:
            return self._lock_y_duplicate
        # A surface should not be mirrored if it's fully in the Y=0 plane,
        # or it has sections on both sides of the plane.
        has_positive_y = any(section.y > 0.05 for section in self.sections)
        has_negative_y = any(section.y < -0.05 for section in self.sections)
        if not has_positive_y and not has_negative_y:
            return False
        if has_positive_y and has_negative_y:
            return False
        return True

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

    def is_simple_tapered(self, accuracy=.05) -> bool:
        return SurfaceTemplates.is_simple_tapered(self, accuracy)

    def taper_ratio(self) -> float:
        if not self.is_simple_tapered():
            raise ValueError('Surface is too complex')
        return self.tip.chord / self.root.chord

    def sweep_angle(self) -> float:
        if not self.is_simple_tapered():
            raise ValueError('Surface is too complex')
        root_25mac = self.root.get_position_at_xc(.25)
        tip_25mac = self.tip.get_position_at_xc(.25)
        sweep = degrees(atan2(tip_25mac.x - root_25mac.x, self.spanwise(self.tip) - self.spanwise(self.root)))
        return sweep

    def add_section(self, section: Section) -> None:
        """Add a new section to the surface and ensures the sections are well-ordered."""
        # Check whether the section is not outside the wing.
        if not self.spanwise(self.root) < self.spanwise(section) < self.spanwise(self.tip): return
        # Check if a section with identical major axis coordinate doesn't already exist.
        if self.spanwise(section) in [self.spanwise(sec) for sec in self.sections]: return

        self.sections.append(section)
        self.sort_sections()

    def add_section_gentle(self, spanwise: float | list[float]) -> Section | list[Section]:
        """Add a new section to the surface without modifying the shape of the surface."""
        if isinstance(spanwise, list):
            scn_list = []
            for spn_i in spanwise:
                scn_list.append(self.add_section_gentle(spn_i))
            return scn_list

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
        return sec

    def sort_sections(self) -> None:
        """Sorts the sections along the major axis of the surface."""
        if len(self.sections) < 2: return
        ref_sec = self.sections[0]
        def pos(section):
            return sqrt((section.y - ref_sec.y) ** 2 + (section.z - ref_sec.z) ** 2)
        self.sections.sort(key=lambda section: pos(section))

    def copy(self) -> 'Surface':
        return copy(self)

    def get_symmetric(self) -> 'Surface':
        """Returns a copy of the surface mirrored about Y-axis."""
        surf = self.copy()
        surf.name = self.name + '_symm'
        reflected_sections = [sec.mirror() for sec in self.sections]
        surf.sections = reflected_sections
        surf._lock_y_duplicate = False
        return surf

    def assert_straight(self):
        if not self.is_straight:
            raise AssertionError('Surface is not straight!')

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

    def clear_mechanization(self) -> None:
        """Removes all mechanization from the surface."""
        self.mechanization = {}
        for sec in self.sections:
            sec.control = None

    def set_mechanization(self, **kwargs: list[tuple[float, float, float]]) -> None:
        """Sets the mechanization of the surface.

        Parameters:
            **kwargs (list[tuple[float, float, float]]): For each type of control a tuple (y_start, y_stop, x_hinge).

        Usage:
            surface_instance.set_mechanization(ailerons=[(1, 2, .7), (3, 3.5, .6)], flaps=[(2.1, 2.9, .6)])

            This will create **ailerons** for ``y`` = <1 : 2> ``hinge`` 0.7 x/c and ``y`` = <3 : 3.5> ``hinge`` 0.6 x/c,
            and **flaps** for ``y`` = <2.1 : 2.9> ``hinge`` 0.6 x/c.
        """
        try:
            self.assert_straight()
        except AssertionError:
            return
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

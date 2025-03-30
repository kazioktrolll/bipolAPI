from .section import Section, Flap, Aileron, Elevator, Control
from .airfoil import Airfoil
from ..to_re_docstring_decorator import to_re_docstring
from ..vector3 import Vector3, AnyVector3
from abc import ABC, abstractmethod
from math import atan, degrees
from typing import Optional


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
                 airfoil: Airfoil = None,):
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

    def mac(self) -> float:
        area = 0
        for i in range(1, len(self.sections)):
            prev = self.sections[i-1]
            curr = self.sections[i]
            area += (prev.chord + curr.chord) * (curr.y - prev.y) / 2
        if self.y_duplicate: area *= 2
        return area / self.span()

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
        secs = []
        if include_start and self.has_section_at(ma_start):
            secs.append(self.get_section_at(ma_start))

        secs += [section for section in self.sections if ma_start < self.major_axis(section) < ma_end]

        if include_end and self.has_section_at(ma_end):
            secs.append(self.get_section_at(ma_end))

        return secs

    def string(self) -> str:
        """Returns the current geometry as a .avl type string."""
        _r = (f"SURFACE\n"
              f"{self.name}\n"
              f"{int(self.mac()*8)} 1.0 {int(self.span()*4)} 1.0\n"
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
                             include_start: bool = True, include_end: bool = False ) -> list[Section]:
        """Returns a list of sections between ``y_start`` and ``y_end``."""
        return super().get_sections_between(ma_start=y_start, ma_end=y_end,
                                            include_start=include_start, include_end=include_end)


class HorizontalSimpleSurface(HorizontalSurface):
    """ A subclass of the ``Surface`` representing a simple, horizontal, trapezoidal lifting surface. """

    def __init__(self,
                 name: str,
                 span: float,
                 chord_length: float,
                 taper_ratio: float = 1,
                 sweep_angle: float = 0,
                 origin_position: AnyVector3 = Vector3.zero(),
                 inclination_angle: float = 0,
                 airfoil=None,
                 ) -> None:
        """
        Parameters:
            span (float): The span of the surface.
            chord_length (float): The mean aerodynamic chord length of the surface.
            origin_position (AnyVector3): Position of the leading edge of the root chord.
            inclination_angle (float): The inclination of the surface, in degrees.
              Zero means horizontal, positive means leading edge up.
            airfoil (Airfoil): The airfoil of the surface.
            taper_ratio (float): The taper ratio of the surface.
            sweep_angle (float): The sweep angle of the surface in degrees.
        """
        if airfoil is None: airfoil = Airfoil.empty()

        self.taper_ratio = taper_ratio
        self.sweep_angle = sweep_angle
        self.inclination = inclination_angle

        root, tip = HorizontalSimpleSurface.create_geometry(chord_length, span, taper_ratio, sweep_angle,
                                                            inclination_angle, airfoil)
        super().__init__(name=name, sections=[root, tip], y_duplicate=True,
                         origin_position=origin_position, airfoil=airfoil)

        self.mechanization: dict[str, list[tuple[float, float, float]]] = {}

    @classmethod
    def create_geometry(cls, chord_length: float, span: float,
                        taper_ratio: float, sweep_angle: float,
                        inclination: float,
                        airfoil: Airfoil
                        ) -> tuple[Section, Section]:
        """
        Returns the root and tip Sections generated based on input parameters.

        Parameters:
            chord_length (float): The mean aerodynamic chord of the surface.
            span (float): The span of the surface.
            taper_ratio (float): The taper ratio of the surface.
            sweep_angle (float): The sweep angle of the surface in degrees.
            inclination (float): The inclination of the surface, in degrees.
            airfoil (Airfoil): The airfoil of the surface.

        Returns:
            Root and tip Sections, in that order.
        """

        # Calculate position and chord for both root and tip sections.
        root_chord = 2 * chord_length / (1 + taper_ratio)
        chord = lambda y: root_chord * (1 - (1 - taper_ratio) * 2 * y / span)
        from math import radians, tan
        mac025 = lambda y: root_chord * .25 + y * tan(radians(sweep_angle))
        leading_edge_y = lambda y: mac025(y) - chord(y) * .25

        root = Section((0, 0, 0), chord(0), inclination, airfoil)
        tip = Section((leading_edge_y(span / 2), span / 2, 0.0), chord(span / 2),
                      inclination, airfoil)

        return root, tip

    def set_mechanization(self,
                          **kwargs: list[tuple[float, float, float]]
                          ) -> None:
        """Sets the mechanization of the surface.

        Parameters:
            **kwargs (list[tuple[float, float, float]]): For each type of control a tuple (y_start, y_stop, x_hinge).

        Usage:
            surface_instance.set_mechanization(ailerons=[(1, 2, .7), (3, 3.5, .6)], flaps=[(2.1, 2.9, .6)])

            This will create **ailerons** for ``y`` = <1 : 2> ``hinge`` 0.7 x/c and ``y`` = <3 : 3.5> ``hinge`` 0.6 x/c,
            and **flaps** for ``y`` = <2.1 : 2.9> ``hinge`` 0.6 x/c.
        """
        if self.mechanization: raise ValueError("The surface {} already has mechanization!".format(self.name))
        self.mechanization = kwargs

        for key, value in kwargs.items():
            key = key.lower()
            try: mech_type = {"ailerons": Aileron, "flaps": Flap, "elevators":Elevator}[key]
            except KeyError: raise ValueError(f"Unknown mechanism type: {key}")
            # To add a control surface in AVL, you add a control surface to a section,
            # and it is valid up to the next section.
            for start, end, hinge_x in value:
                # Ensure there is a ``Section`` at 'y' == 'start' and 'end'.
                if not self.has_section_at(start): self.add_section_gentle(start)
                if not self.has_section_at(end): self.add_section_gentle(end)
                # Add ``Control`` to every Section between 'start' and 'end'.
                sections = self.get_sections_between(start, end, include_end=True)
                for section in sections:
                    if section.has_control: raise Exception("A section already has a control surface!")
                    section.control = mech_type(x_hinge=hinge_x)

    def get_symmetric(self) -> 'HorizontalSimpleSurface':
        """Returns a new instance of HorizontalSimpleSurface reflected about the y-axis."""
        surf = super().get_symmetric()
        assert isinstance(surf, HorizontalSimpleSurface)
        sym_controls = {}
        for k, list_of_ranges in surf.mechanization.items():
            sym_controls[k] = [(-s, -e, xc) for s, e, xc in list_of_ranges]
        surf.mechanization = sym_controls
        return surf

    @classmethod
    def from_complex(cls, surface: HorizontalSurface, accuracy=.05) -> Optional['HorizontalSimpleSurface']:
        root = surface.sections[0]
        tip = surface.sections[-1]

        leading_edge_x_equation = lambda y: root.x + y/tip.y * (tip.x - root.x)
        leading_edge_z_equation = lambda y: root.z + y/tip.y * (tip.z - root.z)
        chord_equation = lambda y: root.chord + y/tip.y * (tip.chord - root.chord)
        inc = root.inclination

        for section in surface.sections:
            y = section.y
            le = section.leading_edge_position
            c = section.chord
            if abs((le.x - leading_edge_x_equation(y)) / c) > accuracy: return None
            if abs((le.z - leading_edge_z_equation(y)) / c) > accuracy: return None
            if abs((c - chord_equation(y)) / c) > accuracy: return None
            if section.inclination != inc: return None

        tr = tip.chord / root.chord
        sa = degrees(atan(abs(
            (root.get_position_at_xc(.25).x - tip.get_position_at_xc(.25).x) / (tip.y - root.y)
        )))

        return cls(
            surface.name, surface.span(), surface.mac(), tr, sa, surface.origin_position, inc, surface.airfoil
        )


class VerticalSimpleSurface(Surface):
    """
    A class representing a single lifting surface of the aircraft, oriented more-or-less vertically.

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


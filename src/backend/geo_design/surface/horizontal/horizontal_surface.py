from ..surface import Surface
from ...section import Section, Flap, Aileron, Elevator
from ...airfoil import Airfoil
from ....vector3 import Vector3, AnyVector3
from math import degrees, atan


class HorizontalSurface(Surface):
    """
    A class representing a single lifting surface of the aircraft, oriented more-or-less horizontally.

    Attributes:
        name (str): The name of the lifting surface.
        y_duplicate (bool): Whether the lifting surface should be mirrored about Y-axis.
        origin_position (Vector3): Position of the leading edge of the root chord.
        airfoil (Airfoil): The airfoil of the surface.
        sections (list[Section]): The sections of the surface. It is always sorted left wingtip-to-right wingtip.
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
        self.mechanization = {}

    @classmethod
    def simple_tapered(cls,
                       name: str,
                       span: float,
                       chord_length: float,
                       taper_ratio: float = 1,
                       sweep_angle: float = 0,
                       origin_position: AnyVector3 = Vector3.zero(),
                       inclination_angle: float = 0,
                       airfoil=None,) -> 'HorizontalSurface':
        """
        Creates a ``HorizontalSurface`` based on parameters of a simple tapered wing.

        Parameters:
            name (str): The name of the lifting surface.
            span (float): The span of the surface.
            chord_length (float): The mean aerodynamic chord length of the surface.
            origin_position (AnyVector3): Position of the leading edge of the root chord.
            inclination_angle (float): The inclination of the surface, in degrees.
              Zero means horizontal, positive means leading edge up.
            airfoil (Airfoil): The airfoil of the surface.
            taper_ratio (float): The taper ratio of the surface.
            sweep_angle (float): The sweep angle of the surface in degrees.
        """

        # Calculate position and chord for both root and tip sections.
        root_chord = 2 * chord_length / (1 + taper_ratio)
        chord = lambda y: root_chord * (1 - (1 - taper_ratio) * 2 * y / span)
        from math import radians, tan
        mac025 = lambda y: root_chord * .25 + y * tan(radians(sweep_angle))
        leading_edge_y = lambda y: mac025(y) - chord(y) * .25

        root = Section((0, 0, 0), chord(0), inclination_angle, airfoil)
        tip = Section((leading_edge_y(span / 2), span / 2, 0.0), chord(span / 2),
                      inclination_angle, airfoil)

        surf = cls(name=name,
                   sections=[root, tip],
                   y_duplicate=True,
                   origin_position=origin_position,
                   airfoil=airfoil)
        return surf

    @classmethod
    def delta(cls, name: str, span: float, surface_area: float,
              origin_position: AnyVector3 = Vector3.zero(),
              inclination_angle: float = 0.0,
              airfoil: Airfoil = None) -> 'HorizontalSurface':
        """
        Creates a ``HorizontalSurface`` based on parameters of a delta wing.

        :param name: Name of the surface.
        :param span: Span of the surface in meters.
        :param surface_area: Surface area of the surface in meters squared.
        :param origin_position: Origin position of the surface in meters.
        :param inclination_angle: Inclination angle of the surface in degrees.
        :param airfoil: Airfoil object.
        """
        chord = surface_area / span
        sweep = degrees(atan(3 / 2 * chord / span))
        surf = cls.simple_tapered(name=name, span=span, origin_position=origin_position,
                                  airfoil=airfoil, inclination_angle=inclination_angle,
                                  taper_ratio=0, chord_length=chord, sweep_angle=sweep)
        return surf

    @classmethod
    def double_trapez(cls, name: str,
                      root_chord: float, mid_chord: float, tip_chord: float,
                      mid_offset: AnyVector3, tip_offset: AnyVector3, origin_position: AnyVector3 = Vector3.zero(),
                      inclination_angle: float = 0, airfoil: Airfoil = None) -> 'HorizontalSurface':

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

        surf = cls(name=name, y_duplicate=True, origin_position=origin_position, airfoil=airfoil, sections=[root, mid, tip])
        return surf

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
        if self.mechanization:
            raise ValueError("The surface {} already has mechanization!".format(self.name))
        self.mechanization = kwargs

        for key, value in kwargs.items():
            key = key.lower()
            for mech_type in [Flap, Aileron, Elevator]:
                if mech_type.is_alias(key):
                    break
            else:
                raise ValueError(f"Unknown mechanism type: {key}")
            # To add a control surface in AVL, you add a control surface to a section,
            # and it is valid up to the next section.
            for start, end, hinge_x in value:
                # Ensure there is a ``Section`` at 'y' == 'start' and 'end'.
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

    def get_symmetric(self) -> 'HorizontalSurface':
        """Returns a new instance of HorizontalSurface reflected about the y-axis."""
        surf = super().get_symmetric()
        assert isinstance(surf, HorizontalSurface)
        surf.clear_controls()
        surf.mechanization = {}
        sym_controls = {}
        for k, list_of_ranges in self.mechanization.items():
            sym_controls[k] = [(-e, -s, xc) for s, e, xc in list_of_ranges]
        surf.set_mechanization(**sym_controls)
        return surf

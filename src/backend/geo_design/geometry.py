from typing import Optional


class Geometry:
    """
    A class representing aircraft's geometry.

    Attributes:
        name (str): The name of the aircraft.
        surface_area (float): The surface area of the aircraft.
        chord_length (float): The mean aerodynamic chord length of the aircraft.
        span_length (float): The wingspan of the aircraft.
        mach (float): The cruise speed of the aircraft as Mach number.
        ref_pos (tuple(float, float, float)): The reference position of the aircraft, ideally the position of the center of mass.
        surfaces (Dict[str, Surface]): The ``Surface`` objects associated with the aircraft.
        wing (Surface|None): The wing of the aircraft. Returns 'None' if the aircraft has no defined wing.
    """
    def __init__(self,
                 name: str,
                 chord_length: float,
                 span_length: float,
                 surface_area: float = 0,
                 mach: float = 0,
                 ref_pos: tuple[float, float, float] = (.0, .0, .0)):
        """
        Parameters:
            name (str): The name of the aircraft.
            chord_length (float): The mean aerodynamic chord length of the aircraft.
            span_length (float): The wingspan of the aircraft.
            surface_area (float): The surface area of the aircraft. If not given, will be calculated as chord*span.
            mach (float): The cruise speed of the aircraft as Mach number.
            ref_pos (Tuple[float, float, float]): The reference position of the aircraft, ideally the position of the center of mass.
        """
        self.name = name
        self.mach = mach
        self.chord_length = chord_length
        self.span_length = span_length
        self.surface_area = surface_area or chord_length * span_length
        self.ref_pos = ref_pos
        self.surfaces: dict[str, Surface] = {}

    def add_surface(self, surface: 'Surface') -> None:
        """Add the given surface to the aircraft's geometry. Is called automatically on Surface creation, no need for manual use."""
        self.surfaces[surface.name] = surface

    @property
    def wing(self) -> Optional['Surface']:
        """The wing of the aircraft. Returns 'None' if the aircraft has no defined wing."""
        try:
            return self.surfaces["Wing"]
        except KeyError:
            return None

    @property
    def h_tail(self) -> Optional['Surface']:
        """The horizontal tail of the aircraft. Returns 'None' if the aircraft has no defined horizontal tail."""
        try:
            return self.surfaces["H_tail"]
        except KeyError:
            return None

    @property
    def v_tail(self) -> Optional['Surface']:
        """The vertical tail of the aircraft. Returns 'None' if the aircraft has no defined vertical tail."""
        try:
            return self.surfaces["V_tail"]
        except KeyError:
            return None


class Surface:
    """
    A class representing a single lifting surface of the aircraft.

    Attributes:
        geometry (Geometry): The top-level object representing the aircraft's geometry.
        name (str): The name of the lifting surface.
        y_duplicate (bool): Whether the lifting surface should be mirrored about Y-axis.
        origin_position (tuple[float, float, float]): Position of the leading edge of the root chord.
        airfoil (list[tuple[float, float]]): The airfoil of the surface.
        inclination_angle (float): The inclination of the surface.
        sections (list[Section]): The sections of the surface. Is always sorted left wingtip-to-right wingtip.
    """
    def __init__(self,
                 geometry: Geometry,
                 name: str,
                 root_section: 'Section',
                 tip_section: 'Section',
                 y_duplicate: bool,
                 origin_position: tuple[float, float, float],
                 airfoil: list[tuple[float, float]],
                 inclination_angle: float):
        """
        Parameters:
            geometry (Geometry): The top-level object representing the aircraft's geometry.
            name (str): The name of the lifting surface.
                If named 'Wing', 'H_tail', 'V_tail' - will be recognized as such by the ``Geometry`` instance.
            root_section (Section): The root section of the surface.
            tip_section (Section): The tip section of the surface.
            y_duplicate (bool): Whether the lifting surface should be mirrored about Y-axis.
                Set ``True`` when defining only one half of a symmetric surface.
            origin_position (tuple[float, float, float]): Position of the leading edge of the root chord.
            airfoil (list[tuple[float, float]]): The airfoil of the surface.
            inclination_angle (float): The inclination of the surface, in degrees. Zero means horizontal, positive means leading edge up.
        """
        self.geometry = geometry
        self.name = name
        self.y_duplicate = y_duplicate
        self.origin_position = origin_position
        self.airfoil = airfoil
        self.inclination_angle = inclination_angle
        self.sections: list[Section] = [root_section, tip_section]
        self.sections.sort(key=lambda section: section.y)
        self.geometry.add_surface(self)

    def add_section(self, section: 'Section'):
        """Add a new section to the surface and ensures the sections are well-ordered."""
        # Check whether the section is not outside the wing.
        if not self.sections[0].y < section.y < self.sections[-1].y: return
        # Check if a section with identical `y` doesn't already exist.
        if section.y in [sec.y for sec in self.sections]: return

        self.sections.append(section)
        self.sections.sort(key=lambda sec: sec.y)

    def add_section_gentle(self, y: float | list[float]):
        """Add a new section to the surface without modifying the shape of the surface."""
        if isinstance(y, list):
            for yi in y:
                self.add_section_gentle(yi)
            return

        assert isinstance(y, (int, float))

        for i, sec in enumerate(self.sections):
            if sec.y >= y:
                prev_sec = self.sections[i - 1]
                next_sec = sec
                break
        else: raise Exception('Incorrect y!')

        # Calculate leading edge position as prev.x + dy * dx
        dy = (y - prev_sec.y) / (next_sec.y - prev_sec.y)
        xle = prev_sec.leading_edge_position[0] + dy * (next_sec.leading_edge_position[0] - prev_sec.leading_edge_position[0])
        zle = prev_sec.leading_edge_position[2] + dy * (next_sec.leading_edge_position[2] - prev_sec.leading_edge_position[2])
        chord = prev_sec.chord + dy * (next_sec.chord - prev_sec.chord)
        sec = Section((xle, y, zle), chord, prev_sec.airfoil)
        self.add_section(sec)

    def get_symmetric(self) -> 'Surface':
        """Returns a copy of the surface mirrored about Y-axis."""
        from copy import copy
        surf = copy(self)
        surf.name = self.name + '_symm' # noqa
        reflected_sections = [sec.mirror() for sec in self.sections]
        surf.sections = reflected_sections
        return surf


class Wing(Surface):
    """ A subclass of the ``Surface`` representing a horizontal wing. """
    @classmethod
    def simple_tapered(cls,
                       geometry: Geometry,
                       origin_position: tuple[float, float, float] = (0,0,0),
                       inclination_angle: float = 0,
                       airfoil=None,
                       taper_ratio: float = 1,
                       sweep_angle: float = 0,
                       ) -> 'Wing':
        """
        Creates a simple trapezoidal, swept, tapered wing.

        Parameters:
            geometry (Geometry): The top-level object representing the aircraft's geometry.
            origin_position (tuple[float, float, float]): Position of the leading edge of the root chord.
            inclination_angle (float): The inclination of the surface, in degrees. Zero means horizontal, positive means leading edge up.
            airfoil (list[tuple[float, float]]): The airfoil of the surface.
            taper_ratio (float): The taper ratio of the wing.
            sweep_angle (float): The sweep angle of the wing in degrees.
        """
        if airfoil is None: airfoil = []
        wingspan = geometry.span_length

        # Calculate position and chord for both root and tip sections.
        root_chord = 2 * geometry.surface_area / wingspan / (1 + taper_ratio)
        chord = lambda y: root_chord * (1 - (1 - taper_ratio) * 2 * y / wingspan)
        from math import radians, tan
        mac025 = lambda y: root_chord * .25 + y * tan(radians(sweep_angle))
        leading_edge_y = lambda y: mac025(y) - chord(y) * .25

        root = Section((0.0, 0.0, 0.0), chord(0), airfoil)
        tip = Section((leading_edge_y(wingspan/2), wingspan/2, 0.0), chord(wingspan/2), airfoil)


        wing = Wing(geometry, name='Wing', root_section=root, tip_section=tip, y_duplicate=True,
                    origin_position=origin_position, airfoil=airfoil, inclination_angle=inclination_angle)
        return wing


class Section:
    """
    A class representing a section of the surface.

    Attributes:
        leading_edge_position (tuple[float, float, float]): Position of the leading edge of the section.
        chord (float): The chord of the section.
        airfoil (list[tuple[float, float]]): The airfoil of the section.
        flap_chord_ratio (float): Chord-wise length of flaps as a percentage of the chord length.
    """
    def __init__(self,
                 leading_edge_position: tuple[float, float, float],
                 chord: float,
                 airfoil: list[tuple[float, float]],
                 flap_chord_ratio: float = 0.0):
        """
        Parameters:
            leading_edge_position (tuple[float, float, float]): Position of the leading edge of the section.
            chord (float): The chord of the section.
            airfoil (list[tuple[float, float]]): The airfoil of the section.
            flap_chord_ratio (float): Chord-wise length of flaps as a percentage of the chord length.
        """
        self.leading_edge_position = leading_edge_position
        self.chord = chord
        self.airfoil = airfoil
        self.flap_chord_ratio = flap_chord_ratio

    def mirror(self) -> 'Section':
        """Returns a copy of self, mirrored about Y-axis."""
        lep = self.leading_edge_position[0], self.leading_edge_position[1] * -1, self.leading_edge_position[2]
        sec = Section(lep, self.chord, self.airfoil, self.flap_chord_ratio)
        return sec

    @property
    def has_flap(self) -> bool:
        """Returns True if the section has a flap."""
        return self.flap_chord_ratio > 0.0

    @property
    def trailing_edge_position(self) -> tuple[float, float, float]:
        """Returns the trailing edge position of the section."""
        return self.leading_edge_position[0] + self.chord, self.leading_edge_position[1], self.leading_edge_position[2]

    @property
    def y(self):
        """Returns the y position of the section."""
        return self.leading_edge_position[1]


from .section import Section, Flap, Aileron


class Surface:
    """
    A class representing a single lifting surface of the aircraft.

    Attributes:
        name (str): The name of the lifting surface.
        chord_length (float): The nominal mean aerodynamic chord length of the lifting surface.
        y_duplicate (bool): Whether the lifting surface should be mirrored about Y-axis.
        origin_position (tuple[float, float, float]): Position of the leading edge of the root chord.
        airfoil (list[tuple[float, float]]): The airfoil of the surface.
        inclination_angle (float): The inclination of the surface.
        sections (list[Section]): The sections of the surface. Is always sorted left wingtip-to-right wingtip.
    """

    def __init__(self,
                 name: str,
                 chord_length: float,
                 root_section: Section,
                 tip_section: Section,
                 y_duplicate: bool,
                 origin_position: tuple[float, float, float],
                 airfoil: list[tuple[float, float]],
                 inclination_angle: float):
        """
        Parameters:
            name (str): The name of the lifting surface.
                If named 'Wing', 'H_tail', 'V_tail' - will be recognized as such by the ``Geometry`` instance.
            chord_length (float): The nominal mean aerodynamic chord length of the lifting surface.
                It is not used for geometry generation, just for calculations.
            root_section (Section): The root section of the surface.
            tip_section (Section): The tip section of the surface.
            y_duplicate (bool): Whether the lifting surface should be mirrored about Y-axis.
                Set ``True`` when defining only one half of a symmetric surface.
            origin_position (tuple[float, float, float]): Position of the leading edge of the root chord.
            airfoil (list[tuple[float, float]]): The airfoil of the surface.
            inclination_angle (float): The inclination of the surface, in degrees. Zero means horizontal, positive means leading edge up.
        """
        self.name = name
        self.chord_length = chord_length
        self.y_duplicate = y_duplicate
        self.origin_position = origin_position
        self.airfoil = airfoil
        self.inclination_angle = inclination_angle
        self.sections: list[Section] = [root_section, tip_section]
        self.sections.sort(key=lambda section: section.y)

    @property
    def span(self) -> float:
        span = self.sections[-1].y - self.sections[0].y
        if self.y_duplicate: span *= 2
        return abs(span)

    def add_section(self, section: Section):
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
        else:
            raise Exception('Incorrect y!')

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
        surf.name = self.name + '_symm'  # noqa
        reflected_sections = [sec.mirror() for sec in self.sections]
        surf.sections = reflected_sections
        return surf

    def has_section_at(self, y: float) -> bool:
        """Returns ``True`` if the surface has a section at ``y``."""
        ys = [section.y for section in self.sections]
        return y in ys

    def get_section_at(self, y: float) -> Section | None:
        """Returns the section at ``y``, if exists, else returns ``None``."""
        if not self.has_section_at(y): return None
        for sec in self.sections:
            if sec.y == y:
                return sec

    def get_sections_between(self, y_start: float, y_end: float,
                             include_start: bool = True, include_end: bool = False
                             ) -> list[Section]:
        """Returns a list of sections between ``y_start`` and ``y_end``."""
        secs = []
        if include_start and self.has_section_at(y_start):
            secs.append(self.get_section_at(y_start))

        secs += [section for section in self.sections if y_start < section.y < y_end]

        if include_end and self.has_section_at(y_end):
            secs.append(self.get_section_at(y_end))

        return secs


class SimpleSurface(Surface):
    """ A subclass of the ``Surface`` representing a simple, trapezoidal lifting surface. """

    def __init__(self,
                 name: str,
                 span: float,
                 chord_length: float,
                 taper_ratio: float = 1,
                 sweep_angle: float = 0,
                 origin_position: tuple[float, float, float] = (0, 0, 0),
                 inclination_angle: float = 0,
                 airfoil=None,
                 ) -> None:
        """
        Parameters:
            span (float): The span of the surface.
            chord_length (float): The mean aerodynamic chord length of the surface.
            origin_position (tuple[float, float, float]): Position of the leading edge of the root chord.
            inclination_angle (float): The inclination of the surface, in degrees. Zero means horizontal, positive means leading edge up.
            airfoil (list[tuple[float, float]]): The airfoil of the surface.
            taper_ratio (float): The taper ratio of the surface.
            sweep_angle (float): The sweep angle of the surface in degrees.
        """
        if airfoil is None: airfoil = []

        self.taper_ratio = taper_ratio
        self.sweep_angle = sweep_angle

        root, tip = SimpleSurface.create_geometry(chord_length, span, taper_ratio, sweep_angle, airfoil, origin_position)
        super().__init__(name=name, chord_length=chord_length, root_section=root, tip_section=tip, y_duplicate=True,
                         origin_position=origin_position, airfoil=airfoil, inclination_angle=inclination_angle)

        self.flaps = []
        self.ailerons = []

    @classmethod
    def create_geometry(cls, chord_length: float, span: float,
                        taper_ratio: float, sweep_angle: float,
                        airfoil: list[tuple[float, float]],
                        origin_position: tuple[float, float, float] = (0, 0, 0)
                        ) -> tuple[Section, Section]:
        """
        Returns the root and tip Sections generated based on input parameters.

        Parameters:
            chord_length (float): The mean aerodynamic chord of the surface.
            span (float): The span of the surface.
            taper_ratio (float): The taper ratio of the surface.
            sweep_angle (float): The sweep angle of the surface in degrees.
            airfoil (list[tuple[float, float]]): The airfoil of the surface.
            origin_position (tuple[float, float, float]): Position of the leading edge of the root chord.

        Returns:
            Root and tip Sections, in that order.
        """

        # Calculate position and chord for both root and tip sections.
        root_chord = 2 * chord_length / (1 + taper_ratio)
        chord = lambda y: root_chord * (1 - (1 - taper_ratio) * 2 * y / span)
        from math import radians, tan
        mac025 = lambda y: root_chord * .25 + y * tan(radians(sweep_angle))
        leading_edge_y = lambda y: mac025(y) - chord(y) * .25

        root = Section(origin_position, chord(0), airfoil)
        tip = Section((leading_edge_y(span / 2), span / 2, 0.0), chord(span / 2), airfoil)

        return root, tip

    def set_mechanization(self,
                          ailerons: list[tuple[float, float, float]] = None,
                          flaps: list[tuple[float, float, float]] = None
                          ) -> None:
        if self.ailerons or self.flaps: raise Exception("The surface {} already has mechanization!".format(self.name))
        # This is not necessary for method's working, but if the function is called with both arguments empty then it's
        # probably due to user's mistake, so it should be raised to attention.
        # Can be bypassed by setting either of the arguments as ``[]``.
        if ailerons is None and flaps is None: raise ValueError("Both ailerons and flaps are be None")

        if ailerons:
            self.ailerons = ailerons
            # To add a control surface in AVL, you add a control surface to a section, and it is valid up to the next section.
            for start, end, hinge_x in self.ailerons:
                # Ensure there is a ``Section`` at 'y' == 'start'.
                if not self.has_section_at(start): self.add_section_gentle(start)
                # Add ``Control`` to every Section between 'start' and 'end', including 'start', excluding 'end'.
                sections = self.get_sections_between(start, end)
                for section in sections:
                    if section.has_control: raise Exception("A section already has a control surface!")
                    section.control = Aileron(x_hinge=hinge_x)
                # Add ``Section`` without ``Control`` at the end.
                if not self.has_section_at(end): self.add_section_gentle(end)

        if flaps:
            self.flaps = flaps
            # To add a control surface in AVL, you add a control surface to a section, and it is valid up to the next section.
            for start, end, x_hinge in self.flaps:
                # Ensure there is a ``Section`` at 'y' == 'start'.
                if not self.has_section_at(start): self.add_section_gentle(start)
                # Add ``Control`` to every Section between 'start' and 'end', including 'start', excluding 'end'.
                sections = self.get_sections_between(start, end)
                for section in sections:
                    if section.has_control: raise Exception("A section already has a control surface!")
                    section.control = Flap(x_hinge=x_hinge)
                # Add ``Section`` without ``Control`` at the end.
                if not self.has_section_at(end): self.add_section_gentle(end)

    def get_symmetric(self) -> 'SimpleSurface':
        surf = super().get_symmetric()
        assert isinstance(surf, SimpleSurface)
        surf.ailerons = [(-s, -e, xc) for s, e, xc in surf.ailerons]
        surf.flaps = [(-s, -e, xc) for s, e, xc in surf.flaps]
        return surf

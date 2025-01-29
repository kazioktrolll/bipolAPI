class Geometry:
    def __init__(self,
                 name: str,
                 surface_area: float,
                 chord_length: float,
                 span_length: float,
                 mach: float = 0,
                 is_symmetric: tuple[bool, bool, bool] = (False, False, False),
                 ref_pos: tuple[float, float, float] = (0.0, 0.0, 0.0),):
        self.name = name
        self.mach = mach
        self.is_symmetric = is_symmetric
        self.surface_area = surface_area
        self.chord_length = chord_length
        self.span_length = span_length
        self.ref_pos = ref_pos
        self.surfaces: dict[str, Surface] = {}


class Surface:
    def __init__(self,
                 geometry: Geometry,
                 name: str,
                 y_duplicate: bool,
                 origin_position: tuple[float, float, float],
                 airfoil: list[tuple[float, float]],
                 inclination: float):
        self.geometry = geometry
        self.name = name
        self.y_duplicate = y_duplicate
        self.origin_position = origin_position
        self.inclination = inclination
        self.airfoil = airfoil
        self.sections: list[Section] = []

    def add_section(self, section: 'Section'):
        self.sections.append(section)
        self.sections.sort(key=lambda sec: sec.y)

    def add_section_gentle(self, y: float | list[float]):
        if isinstance(y, list):
            for yi in y:
                self.add_section_gentle(yi)
            return

        assert isinstance(y, float) or isinstance(y, int)

        for i, sec in enumerate(self.sections):
            if sec.y >= y:
                prev_sec = self.sections[i - 1]
                next_sec = sec
                break
        else: raise Exception('Incorrect y!')

        # Calculate leading edge position as prev.x + y/dy * dx
        xle = prev_sec.leading_edge_position[0] + (y - prev_sec.y) / (next_sec.y - prev_sec.y) * (next_sec.leading_edge_position[0] - prev_sec.leading_edge_position[0])
        zle = prev_sec.leading_edge_position[2] + (y - prev_sec.y) / (next_sec.y - prev_sec.y) * (next_sec.leading_edge_position[2] - prev_sec.leading_edge_position[2])
        chord = prev_sec.chord + (y - prev_sec.y) / (next_sec.y - prev_sec.y) * (next_sec.chord - prev_sec.chord)
        sec = Section((xle, y, zle), chord, prev_sec.airfoil)
        self.add_section(sec)


class Wing(Surface):
    @classmethod
    def simple_tapered(cls,
                       geometry: Geometry,
                       origin_position: tuple[float, float, float] = (0,0,0),
                       inclination: float = 0,
                       airfoil: list[tuple[float, float]] = [],
                       taper_ratio: float = 1,
                       sweep_angle: float = 0,
                       ) -> 'Wing':
        wing = Wing(geometry, 'Wing', True, origin_position, airfoil, inclination)
        wingspan = geometry.span_length

        root_chord = 2 * geometry.surface_area / wingspan / (1 + taper_ratio)
        chord = lambda y: root_chord * (1 - (1 - taper_ratio) * 2 * y / wingspan)
        from math import radians, tan
        mac025 = lambda y: root_chord * .25 + y * tan(radians(sweep_angle))
        leading_edge_y = lambda y: mac025(y) - chord(y) * .25

        wing.sections = [
            Section((0.0, 0.0, 0.0), chord(0), wing.airfoil), # Root
            Section((leading_edge_y(wingspan/2), wingspan/2, 0.0), chord(wingspan/2), wing.airfoil) # Tip
        ]
        return wing


class Section:
    def __init__(self,
                 leading_edge_position: tuple[float, float, float],
                 chord: float,
                 airfoil: list[tuple[float, float]],
                 flap_chord_ratio: float = 0.0):
        self.leading_edge_position = leading_edge_position
        self.chord = chord
        self.airfoil = airfoil
        self.flap_chord_ratio = flap_chord_ratio

    @property
    def has_flap(self) -> bool:
        return self.flap_chord_ratio > 0.0

    @property
    def trailing_edge_position(self) -> tuple[float, float, float]:
        return self.leading_edge_position[0] + self.chord, self.leading_edge_position[1], self.leading_edge_position[2]

    @property
    def y(self):
        return self.leading_edge_position[1]

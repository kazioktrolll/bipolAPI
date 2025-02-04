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

from typing import Optional


class Section:
    """
    A class representing a section of the surface.

    Attributes:
        leading_edge_position (tuple[float, float, float]): Position of the leading edge of the section.
        chord (float): The chord of the section.
        airfoil (list[tuple[float, float]]): The airfoil of the section.
        control (Control): The control surface of the section.
    """

    def __init__(self,
                 leading_edge_position: tuple[float, float, float],
                 chord: float,
                 airfoil: list[tuple[float, float]]):
        """
        Parameters:
            leading_edge_position (tuple[float, float, float]): Position of the leading edge of the section.
            chord (float): The chord of the section.
            airfoil (list[tuple[float, float]]): The airfoil of the section.
        """
        self.leading_edge_position = leading_edge_position
        self.chord = chord
        self.airfoil = airfoil
        self.control: Optional['Control'] = None

    def mirror(self) -> 'Section':
        """Returns a copy of self, mirrored about Y-axis."""
        lep = self.leading_edge_position[0], self.leading_edge_position[1] * -1, self.leading_edge_position[2]
        sec = Section(lep, self.chord, self.airfoil)
        return sec

    @property
    def has_control(self) -> bool:
        """Returns True if the section has a control surface."""
        return self.control is not None

    @property
    def trailing_edge_position(self) -> tuple[float, float, float]:
        """Returns the trailing edge position of the section."""
        return self.leading_edge_position[0] + self.chord, self.leading_edge_position[1], self.leading_edge_position[2]

    @property
    def y(self):
        """Returns the y position of the section."""
        return self.leading_edge_position[1]


class Control:
    """Class representing a control surface attached to a section."""
    def __init__(self, name: str, x_hinge: float, SgnDup: bool,
                 gain: float = 1, xyz_h_vec: tuple[float, float, float] = (0, 0, 0)):
        """
        Parameters:
            name (str): The name of the control surface.
            x_hinge (float): The x/c position of the hinge. If negative, the surface is on the leading edge.
            SgnDup (bool): The sign of the sign of the hinge.
                ``True`` for symmetric deflection, ``False`` for antisymmetric defection.
            gain (float): The gain of the control surface. Defaults to 1.
            xyz_h_vec (tuple[float, float, float]): The xyz position of the hinge. Defaults to (0, 0, 0).
        """
        assert -1 < x_hinge < 1

        self.name = name
        self.x_hinge = x_hinge
        self.SgnDup = SgnDup
        self.gain = gain
        self.xyz_h_vec = xyz_h_vec


class Flap(Control):
    def __init__(self, x_hinge: float):
        """
        Parameters:
            x_hinge (float): The x/c position of the hinge.
        """
        assert 0 < x_hinge < 1
        super().__init__(name='flap', x_hinge=x_hinge, SgnDup=True)


class Aileron(Control):
    def __init__(self, x_hinge: float):
        """
        Parameters:
            x_hinge (float): The x/c position of the hinge.
        """
        assert 0 < x_hinge < 1
        super().__init__(name='aileron', x_hinge=x_hinge, SgnDup=False)
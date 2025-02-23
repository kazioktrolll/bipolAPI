from typing import Optional
from math import tan, radians
from .airfoil import Airfoil


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
                 inclination: float,
                 airfoil: Airfoil):
        """
        Parameters:
            leading_edge_position (tuple[float, float, float]): Position of the leading edge of the section.
            chord (float): The chord of the section.
            inclination (float): The total inclination of the section, in degrees.
            airfoil (Airfoil): The airfoil of the section.
        """
        self.leading_edge_position = leading_edge_position
        self.chord = chord
        self.inclination = inclination
        self.airfoil = airfoil
        self.control: Optional['Control'] = None

    def mirror(self) -> 'Section':
        """Returns a copy of self, mirrored about Y-axis."""
        lep = self.leading_edge_position[0], self.leading_edge_position[1] * -1, self.leading_edge_position[2]
        sec = Section(lep, self.chord, self.inclination, self.airfoil)
        sec.control = self.control.copy() if self.control is not None else None
        return sec

    @property
    def has_control(self) -> bool:
        """Returns True if the section has a control surface."""
        return self.control is not None

    def get_position_at_xc(self, xc: float) -> tuple[float, float, float]:
        """Returns the position of the section at the given x/c."""
        return (self.leading_edge_position[0] + self.chord * xc,
                self.leading_edge_position[1],
                self.leading_edge_position[2] - self.chord * xc * tan(radians(self.inclination)))

    @property
    def trailing_edge_position(self) -> tuple[float, float, float]:
        """Returns the trailing edge position of the section."""
        return self.leading_edge_position[0] + self.chord, self.leading_edge_position[1], self.leading_edge_position[2] - self.chord * tan(radians(self.inclination))

    @property
    def y(self):
        """Returns the y position of the section."""
        return self.leading_edge_position[1]

    @property
    def z(self):
        """Returns the z position of the section."""
        return self.leading_edge_position[2]

    def string(self) -> str:
        """Returns the current geometry as a .avl type string."""
        _r = (f"\n"
              f"SECTION\n"
              f"{self.leading_edge_position[0]} {self.leading_edge_position[1]} {self.leading_edge_position[2]} "
              f"{self.chord} {self.inclination}\n")
        _r += self.airfoil.string()
        if self.has_control:
            _r += self.control.string()
        return _r


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

    def copy(self) -> 'Control':
        """Returns a copy of this control surface."""
        return Control(self.name, self.x_hinge, self.SgnDup, self.gain, self.xyz_h_vec)

    def string(self) -> str:
        """Returns the current geometry as a .avl type string."""
        return ("CONTROL\n"
                f"{self.name} {self.gain} {self.x_hinge} "
                f"{self.xyz_h_vec[0]} {self.xyz_h_vec[1]} {self.xyz_h_vec[2]} "
                f"{"+1" if self.SgnDup else "-1"}\n")


class Flap(Control):
    def __init__(self, x_hinge: float):
        """
        Parameters:
            x_hinge (float): The x/c position of the hinge.
        """
        assert 0 < x_hinge < 1
        super().__init__(name='flap', x_hinge=x_hinge, SgnDup=True)

    def copy(self) -> 'Flap':
        """Returns a copy of this flap."""
        return Flap(self.x_hinge)


class Aileron(Control):
    def __init__(self, x_hinge: float):
        """
        Parameters:
            x_hinge (float): The x/c position of the hinge.
        """
        assert 0 < x_hinge < 1
        super().__init__(name='aileron', x_hinge=x_hinge, SgnDup=False)

    def copy(self) -> 'Aileron':
        """Returns a copy of this aileron."""
        return Aileron(self.x_hinge)

class Elevator(Control):
    def __init__(self, x_hinge: float):
        """
        Parameters:
            x_hinge (float): The x/c position of the hinge.
        """
        assert 0 < x_hinge < 1
        super().__init__(name='elevator', x_hinge=x_hinge, SgnDup=True)

    def copy(self) -> 'Elevator':
        """Returns a copy of this aileron."""
        return Elevator(self.x_hinge)
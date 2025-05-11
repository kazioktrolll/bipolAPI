"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from typing import TypeVar
from math import tan, radians
from .airfoil import Airfoil
from ..vector3 import Vector3, AnyVector3

T = TypeVar('T', bound='Control')


class Section:
    """
    A class representing a section of the surface.

    Attributes:
        leading_edge_position (Vector3): Position of the leading edge of the section.
        chord (float): The chord of the section.
        airfoil (list[tuple[float, float]]): The airfoil of the section.
        control (Control): The control surface of the section.
    """

    def __init__(self,
                 leading_edge_position: AnyVector3,
                 chord: float,
                 inclination: float,
                 airfoil: Airfoil = None,
                 control: 'Control' = None) -> None:
        """
        Parameters:
            leading_edge_position (AnyVector3): Position of the leading edge of the section.
            chord (float): The chord of the section.
            inclination (float): The total inclination of the section, in degrees.
            airfoil (Airfoil): The airfoil of the section.
        """
        self.leading_edge_position = Vector3(*leading_edge_position)
        self.chord = chord
        self.inclination = inclination
        self.airfoil = airfoil or Airfoil.empty()
        self.control = control

    def __repr__(self) -> str:
        return f"Section at: {self.leading_edge_position.tuple()} x {self.chord}, control: {self.control.__repr__()}"

    def mirror(self) -> 'Section':
        """Returns a copy of self, mirrored about Y-axis."""
        lep = self.leading_edge_position.scale((1, -1, 1))
        sec = Section(lep, self.chord, self.inclination, self.airfoil)
        sec.control = self.control.copy() if self.control is not None else None
        return sec

    @property
    def has_control(self) -> bool:
        """Returns True if the section has a control surface."""
        return self.control is not None

    def get_position_at_xc(self, xc: float) -> Vector3:
        """Returns the position of the section at the given x/c."""
        return self.leading_edge_position + (self.chord * xc,
                                             0,
                                             -self.chord * xc * tan(radians(self.inclination)))

    @property
    def trailing_edge_position(self) -> Vector3:
        """Returns the trailing edge position of the section."""
        return self.get_position_at_xc(1)

    @property
    def x(self):
        """Returns the y position of the section."""
        return self.leading_edge_position.x

    @property
    def y(self):
        """Returns the y position of the section."""
        return self.leading_edge_position.y

    @property
    def z(self):
        """Returns the z position of the section."""
        return self.leading_edge_position.z

    def string(self) -> str:
        """Returns the current geometry as a .avl type string."""
        _r = (f"\n"
              f"SECTION\n"
              f"{self.leading_edge_position.avl_string} {self.chord} {self.inclination}\n")
        _r += self.airfoil.string()
        if self.has_control:
            _r += self.control.string()
        return _r


class Control:
    class_name: str
    """Class representing a control surface attached to a section."""

    def __init__(self, x_hinge: float, SgnDup: bool,
                 gain: float = 1, color: str = 'green', name: str = None) -> None:
        """
        Parameters:
            name (str): The name of the control surface.
            x_hinge (float): The x/c position of the hinge. If negative, the surface is on the leading edge.
            SgnDup (bool): The sign of the sign of the hinge.
                ``True`` for symmetric deflection, ``False`` for antisymmetric defection.
            gain (float): The gain of the control surface. Defaults to 1.
            color (str): The color of the control surface. Defaults to 'green'.
        """
        assert -1 < x_hinge < 1

        self.x_hinge = x_hinge
        self.SgnDup = SgnDup
        self.gain = gain
        self.color = color
        self.instance_name = name

    def __repr__(self) -> str:
        return self.name

    def copy(self: T) -> T:
        """Returns a copy of this control surface."""
        return self.__class__(**self.__dict__)

    def string(self) -> str:
        """Returns the current geometry as a .avl type string."""
        return ("CONTROL\n"
                f"{self.name} {self.gain} {self.x_hinge} 0. 0. 0. {"+1" if self.SgnDup else "-1"}\n")

    def is_equal_to(self, other) -> bool:
        """Returns True if the two control surfaces are of the same type and should be connected."""
        if not isinstance(other, Control): return False
        return (self.name == other.name
                and self.gain == other.gain
                and self.x_hinge == other.x_hinge
                and self.SgnDup == other.SgnDup
                and self.color == other.color)

    @property
    def name(self):
        try:
            return self.class_name
        except AttributeError:
            return self.instance_name

    @classmethod
    def is_alias(cls, name: str) -> bool:
        name = name.lower()
        return name == cls.class_name or name + 's' == cls.class_name


class PreDefControl(Control):
    """An interface for pre-defined types of control surfaces."""

    def __init__(self, x_hinge: float, SgnDup: bool,
                 gain: float = 1, color: str = 'green') -> None:
        super().__init__(x_hinge, SgnDup, gain, color)
        assert self.class_name is not None

    def copy(self: T) -> T:
        return self.__class__(self.x_hinge)


class Flap(PreDefControl):
    class_name = 'flaps'

    def __init__(self, x_hinge: float):
        """
        Parameters:
            x_hinge (float): The x/c position of the hinge.
        """
        assert 0 < x_hinge < 1
        super().__init__(x_hinge=x_hinge, SgnDup=True, color='yellow')


class Aileron(PreDefControl):
    class_name = 'ailerons'

    def __init__(self, x_hinge: float):
        """
        Parameters:
            x_hinge (float): The x/c position of the hinge.
        """
        assert 0 < x_hinge < 1
        super().__init__(x_hinge=x_hinge, SgnDup=False)


class Elevator(PreDefControl):
    class_name = 'elevators'

    def __init__(self, x_hinge: float):
        """
        Parameters:
            x_hinge (float): The x/c position of the hinge.
        """
        assert 0 < x_hinge < 1
        super().__init__(x_hinge=x_hinge, SgnDup=True, color='green3')

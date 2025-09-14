"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from typing import Union

Tuple3 = tuple[float, float, float]
AnyVector3 = Union['Vector3', Tuple3]


def _is_tuple3(var) -> bool:
    return isinstance(var, tuple) and len(var) == 3 and all(isinstance(val, (int, float)) for val in var)


class Vector3:
    def __init__(self, x: float, y: float, z: float) -> None:
        """An object representing a 3-dimensional vector. Mimics a tuple, has some additional methods."""
        if not all(isinstance(val, (int, float)) for val in (x, y, z)):  # Check if all arguments are numeric
            raise TypeError("All arguments must be numeric")
        self.x, self.y, self.z = x, y, z

    @classmethod
    def zero(cls) -> 'Vector3':
        """Returns a zero vector."""
        return cls(0, 0, 0)

    def __repr__(self) -> str:
        return f"Vector3({self.x}, {self.y}, {self.z})"

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def tuple(self) -> Tuple3:
        """Returns x, y, z as a tuple."""
        return self.x, self.y, self.z

    def copy(self) -> 'Vector3':
        """Returns a copy of this vector."""
        return Vector3(*self)

    def __add__(self, other: AnyVector3) -> 'Vector3':
        if _is_tuple3(other): other = Vector3(*other)
        assert isinstance(other, Vector3)
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, other: int | float) -> 'Vector3':
        assert isinstance(other, (int, float))
        return Vector3(self.x * other, self.y * other, self.z * other)

    def __sub__(self, other: AnyVector3) -> 'Vector3':
        if _is_tuple3(other): other = Vector3(*other)
        assert isinstance(other, Vector3)
        return self.__add__(other * -1)

    def __eq__(self, other: AnyVector3) -> bool:
        if _is_tuple3(other): other = Vector3(*other)
        if not isinstance(other, Vector3):
            return NotImplemented
        return self.x == other.x and self.y == other.y and self.z == other.z

    def scale(self, other: AnyVector3) -> 'Vector3':
        """Returns a copy of self scaled by the vector so that ``new``.x = ``self``.x * ``scale``.x etc.
        From the mathematical point of view it's the same as ``self`` * ``other`` ^T."""
        other = Vector3(*other)
        return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)

    def cross_product(self, other: AnyVector3) -> 'Vector3':
        """Returns cross-product of two vectors."""
        return Vector3(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z, self.x * other.y - self.y * other.x)

    def length(self) -> float:
        """Returns the length of the vector."""
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    @property
    def avl_string(self) -> str:
        """Returns a string 'x y z'."""
        return f"{self.x} {self.y} {self.z}"

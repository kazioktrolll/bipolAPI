from typing import Union

Tuple3 = tuple[float, float, float]
AnyVector3 = Union['Vector3', Tuple3]


def is_tuple3(var) -> bool:
    return isinstance(var, tuple) and len(var) == 3 and all(isinstance(val, (int, float)) for val in var)


class Vector3:
    def __init__(self, x: float, y: float, z: float) -> None:
        """An object representing a 3-dimensional vector."""
        if not all(isinstance(val, (int, float)) for val in (x, y, z)): raise TypeError("All arguments must be numeric")
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
        if is_tuple3(other): other = Vector3(*other)
        assert isinstance(other, Vector3)
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, other: int | float) -> 'Vector3':
        assert isinstance(other, (int, float))
        return Vector3(self.x * other, self.y * other, self.z * other)

    def __sub__(self, other: AnyVector3) -> 'Vector3':
        if is_tuple3(other): other = Vector3(*other)
        assert isinstance(other, Vector3)
        return self.__add__(other * -1)

    def scale(self, other: AnyVector3) -> 'Vector3':
        other = Vector3(*other)
        return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)

    @property
    def avl_string(self) -> str:
        """Returns a string 'x y z'."""
        return f"{self.x} {self.y} {self.z}"

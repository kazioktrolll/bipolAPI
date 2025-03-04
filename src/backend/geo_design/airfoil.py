from pathlib import Path
import re


def is_number(s: str):
    """Checks if a string is a valid number."""
    try:
        float(s)
        return True
    except ValueError:
        return False

def are_numbers(ls: list[str]):
    """Checks if a list of strings are all valid numbers."""
    for s in ls:
        if not is_number(s):
            return False
    return True

def valid_naca(naca: str):
    """Checks if a string is a valid 4-digit symmetric NACA code."""
    return re.fullmatch(r"\d\d\d\d", naca)


class Airfoil:
    """
    A class representing an airfoil geometry.

    Attributes:
            name (str): The name of the airfoil.
            points (Optional list[tuple[float, float]]): A list of points defining the airfoil geometry.
                ``None`` if the airfoil is not point-defined.
            naca (str): The NACA code of the airfoil. ``None`` if the airfoil is not defined using NACA code.
            active_range (tuple[float, float]): The active range of the airfoil.
    """
    points: list[tuple[float, float]] | None
    naca: str | None
    name: str
    active_range: tuple[float, float]

    def __init__(self, name: str, points:list[tuple[float, float]]|None, naca:str|None, active_range:tuple[float, float]):
        """
        Parameters:
            name (str): The name of the airfoil.
            points (Optional list[tuple[float, float]]): A list of points defining the airfoil geometry.
                ``None`` if the airfoil is not point-defined.
            naca (str): The NACA code of the airfoil. ``None`` if the airfoil is not defined using NACA code.
            active_range (tuple[float, float]): The active range of the airfoil.
        """
        self.name = name
        self.points = points
        self.naca = naca
        self.active_range = active_range

    @classmethod
    def from_file(cls, path: Path | str, name: str = None, active_range=(0.0, 1.0)) -> 'Airfoil':
        """Creates an Airfoil object using geometry from a file."""
        if isinstance(path, str): path = Path(path)
        name = name or path.stem
        with open(path) as f: raw_lines = f.readlines()

        lines = []
        for line in raw_lines:
            line = line.replace('\n', '')
            line = line.strip()
            line = line.replace('\t', ',')
            line = line.replace(' ', ',')
            line = re.split(r',+', line)
            line = [s for s in line if s]
            lines.append(line)


        data: list[tuple[float, float]] = []
        for i, line in enumerate(lines):
            if not line: continue
            if not are_numbers(line) or len(line) != 2: continue

            new_line = (float(line[0]), float(line[1]))
            if not (-1 < new_line[0] < 1) or not (-1 < new_line[1] < 1): continue
            data.append(new_line)

        positive = [(x,y) for x,y in data if y>=0]
        positive.sort(key=lambda p: -p[0])
        negative = [(x,y) for x,y in data if y<0]
        negative.sort(key=lambda p: p[0])
        sorted_data = positive + negative

        if len(sorted_data) < 3: raise ValueError("Incorrect input file!")

        af = Airfoil(name, points=sorted_data, naca=None, active_range=active_range)
        return af

    @classmethod
    def from_naca(cls, naca: str, active_range=(0.0, 1.0)) -> 'Airfoil':
        """Creates an Airfoil object from NACA code."""
        if not valid_naca(naca): raise ValueError("Wrong NACA code")
        af = Airfoil(name=naca, points=None, naca=naca, active_range=active_range)
        return af

    @classmethod
    def empty(cls) -> 'Airfoil':
        """Creates a flat-plate Airfoil."""
        af = Airfoil(name="Empty", points=None, naca=None, active_range=(0.0, 1.0))
        return af

    def string(self) -> str:
        """Returns the current geometry as a .avl type string."""
        if self.points is None and self.naca is None:
            print("Empty Airfoil is converted to a string!")
            return ""

        if self.naca:
            return f"NACA {self.active_range[0]} {self.active_range[1]}\n{self.naca}\n"

        _r = f"AIRFOIL {self.active_range[0]} {self.active_range[1]}\n"
        for x, y in self.points:
            _r += f"{x} {y}\n"
        return _r

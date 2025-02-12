from pathlib import Path
import re


def is_number(s: str):
    try:
        float(s)
        return True
    except ValueError:
        return False

def are_numbers(ls: list[str]):
    for s in ls:
        if not is_number(s):
            return False
    return True

def valid_naca(naca: str):
    if not len(naca) == 4: return False
    for char in naca:
        if char not in '0123456789': return False
    return True


class Airfoil:
    points: list[tuple[float, float]] | None
    naca: str | None
    name: str
    active_range: tuple[float, float]

    @classmethod
    def from_file(cls, path: Path, name: str, active_range=(0.0, 1.0)) -> 'Airfoil':
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

        af = Airfoil()
        af.name = name
        af.points = sorted_data
        af.naca = None
        af.active_range = active_range
        return af

    @classmethod
    def from_naca(cls, naca: str, active_range=(0.0, 1.0)) -> 'Airfoil':
        if not valid_naca(naca): raise ValueError("Wrong NACA code")
        af = Airfoil()
        af.naca = naca
        af.name = naca
        af.points = None
        af.active_range = active_range
        return af

    @classmethod
    def empty(cls) -> 'Airfoil':
        af = Airfoil()
        af.naca = None
        af.points = None
        af.name = "Empty"
        return af

    def string(self) -> str:
        if self.points is None and self.naca is None:
            print("Empty Airfoil is converted to a string!")
            return ""

        if self.naca:
            return f"NACA {self.active_range[0]} {self.active_range[1]}\n{self.naca}"

        _r = f"AIRFOIL {self.active_range[0]} {self.active_range[1]}\n"
        for x, y in self.points:
            _r += f"{x} {y}\n"
        return _r

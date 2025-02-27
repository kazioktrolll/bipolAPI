from pathlib import Path
from typing import Any
from .geometry import Geometry
from .surface import Surface, SurfaceCreator, SimpleSurface, VerticalSurface
from .section import Section, Control
from .airfoil import Airfoil
from ..vector3 import Vector3


class GeometryGenerator:
    @classmethod
    def default(cls) -> Geometry:
        wing = SimpleSurface(name='wing', span=8, chord_length=1)
        h_tail = SimpleSurface(name='h_tail', span=1, chord_length=1, origin_position=(4, 0, 1))
        v_tail = VerticalSurface(
            name='v_tail',
            chord_length=.9,
            sections=[
                Section((0,0,0), 1.1, 0),
                Section((.2,0,.5), .9, 0),
            ],
            origin_position=(3.8, 0, .5),
            y_duplicate=False
        )
        g = Geometry(
            name="default",
            chord_length=wing.chord_length,
            span_length=wing.span(),
            surfaces=[wing, h_tail, v_tail],
            surface_area=wing.chord_length * wing.span(),
        )
        return g

    @classmethod
    def from_avl(cls, path: Path | str) -> Geometry:
        """Creates a Geometry object based on .avl file."""
        return FromAvl.load(path)


class FromAvl:
    @classmethod
    def load(cls, path: Path | str) -> Geometry:
        """Creates a Geometry object based on .avl file."""
        if isinstance(path, str): path = Path(path)
        with open(path) as f: raw_lines = f.readlines()
        lines = cls.format_lines(raw_lines)
        return cls.handle_top_level(lines)

    @classmethod
    def format_lines(cls, raw_lines: list[str]) -> list[str]:
        """Returns a list of lines after formatting."""
        lines = []
        for line in raw_lines:
            if '#' in line or '!' in line: continue
            if '|' in line: line = line.split('|')[0]
            line = line.strip()
            if not line: continue
            lines.append(line)
        return lines

    @classmethod
    def split_into_blocks(cls, lines: list[str], keywords: tuple[str, ...]) -> list[list[str]]:
        """Splits lines into blocks, each block starting with one of the given keywords."""
        current_block = None
        blocks = []

        for line in lines:
            if line in keywords:
                if current_block is not None: blocks.append(current_block)
                current_block = [line]
                continue
            if current_block is not None: current_block.append(line)
        else:
            if current_block is not None: blocks.append(current_block)
        return blocks

    @classmethod
    def handle_top_level(cls, lines: list[str]) -> Geometry:
        """Returns a Geometry object based on .avl file."""
        # Reading
        name = lines.pop(0)
        mach = float(lines.pop(0))
        syms = tuple(map(float, lines.pop(0).split()))
        refs = tuple(map(float, lines.pop(0).split()))
        ref_pos = tuple(map(float, lines.pop(0).split()))
        next_line = lines.pop(0)
        try:
            CDp = float(next_line)
        except ValueError:
            CDp = 0
            lines.insert(0, next_line)
        geometry_data = {
            'name': name,
            'chord_length': refs[1],
            'span_length': refs[2],
            'surface_area': refs[0],
            'mach': mach,
            'ref_pos': ref_pos,
            'surfaces': []
        }

        blocks = cls.split_into_blocks(lines, ('SURFACE', 'BODY'))
        for block in blocks:
            if block[0] == 'SURFACE': geometry_data['surfaces'].append(cls.handle_surface_level(block[1:]))
            if block[0] == 'BODY': cls.error('GAVL does not support BODY. The block is being skipped.')

        return Geometry(**geometry_data)

    @classmethod
    def handle_surface_level(cls, block: list[str]) -> Surface:
        """Returns a Surface based on .avl description lines."""
        surface_data: dict[str, Any] = {
            'name': None,
            'chord_length': None,
            'sections': [],
            'y_duplicate': False,
            'origin_position': None,
            'airfoil': None,
        }
        name = block.pop(0)
        surface_data['name'] = name
        Nchord_etc = block.pop(0)  # TODO: implement?

        keywords = (
            'COMPONENT',
            'INDEX',
            'YDUPLICATE',
            'SCALE',
            'TRANSLATE',
            'ANGLE',
            'NOWAKE',
            'NOALBE',
            'NOLOAD',
            'CDCL',
            'SECTION'
        )

        blocks = cls.split_into_blocks(block, keywords)
        scale = (1,1,1)
        angle = 0
        for b in blocks:
            match b[0]:
                case kw if kw in ('COMPONENT', 'INDEX'):
                    cls.error(f"{kw}")
                case 'YDUPLICATE':
                    if float(b[1]) == 0.0:
                        surface_data['y_duplicate'] = True
                    else:
                        cls.error(f"YDUPLICATE cannot be non-zero!")  # TODO: fix?
                case 'SCALE':
                    scale = tuple(map(float, b[1].split()))
                case 'TRANSLATE':
                    vals = map(float, b[1].split())
                    surface_data['origin_position'] = Vector3(*vals)
                case 'ANGLE':
                    angle = float(b[1])
                case kw if kw in ('NOWAKE', 'NOALBE', 'NOLOAD'):
                    cls.error(f"{kw}")
                case 'CDCL':
                    cls.error("CDCL")
                case 'SECTION':
                    surface_data['sections'].append(cls.handle_section_level(b[1:], scale, angle))

        surface_data['airfoil'] = surface_data['sections'][0].airfoil
        return SurfaceCreator.UnknownSurface(**surface_data)

    @classmethod
    def handle_section_level(cls, block: list[str], scale=(1,1,1), angle=0) -> Section:
        """Returns a Section based on .avl description lines."""
        vals = list(map(float, block.pop(0).split()))
        section_data = {
            'leading_edge_position': Vector3(*vals[:3]).scale(scale),
            'chord': vals[3],
            'inclination': vals[4] + angle,
            'airfoil': None,
            'control': None
        }

        for b in cls.split_into_blocks(block, ('NACA', 'AIRFOIL', 'AFILE', 'CONTROL', 'DESIGN')):
            match b[0]:
                case 'NACA':
                    section_data['airfoil'] = Airfoil.from_naca(naca=b[1])
                case 'AIRFOIL':
                    # TODO: do
                    pass
                case 'AFILE':
                    section_data['airfoil'] = Airfoil.from_file(path=b[1])
                case 'CONTROL':
                    section_data['control'] = cls.handle_control_level(b[1:])
                case 'DESIGN':
                    cls.error("DESIGN")
        return Section(**section_data)

    @classmethod
    def handle_control_level(cls, block: list[str]) -> Control:
        """Returns a Control based on .avl description lines."""
        vals = block.pop(0).split()
        name = vals.pop(0)
        vals = list(map(float, vals))
        control_data = {
            'name': name,
            'gain': vals[0],
            'x_hinge': vals[1],
            'xyz_h_vec': vals[2:5],
            'SgnDup': vals[5]
        }
        return Control(**control_data)

    @classmethod
    def error(cls, message: str) -> None:
        """Handles a Syntax Error in the .avl file."""
        print(message)  # Temporary

"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from pathlib import Path
from typing import Any

from .airfoil import Airfoil
from .geometry import Geometry
from .section import Section, Control
from .surface import Surface, SurfaceCreator, HorizontalSurface, VerticalSurface
from ..vector3 import Vector3


class GeometryGenerator:
    @classmethod
    def empty(cls) -> 'Geometry':
        g = Geometry(
            name='Empty',
            chord_length=0,
            span_length=0
        )
        return g

    @classmethod
    def default(cls) -> Geometry:
        wing = HorizontalSurface.simple_tapered(name='Wing', span=8, chord_length=1, airfoil=Airfoil.from_naca('2415'))
        wing.set_mechanization(ailerons=[(3, 4, .8)], flaps=[(2.3, 2.8, .6)])
        h_tail = HorizontalSurface.simple_tapered(name='H Tail', span=2, chord_length=1, origin_position=(4, 0, 1), airfoil=Airfoil.from_naca('0012'))
        h_tail.set_mechanization(elevators=[(0, 1, .8)])
        v_tail = VerticalSurface(
            name='V Tail',
            sections=[
                Section((0, 0, 0), 1.1, 0, airfoil=Airfoil.from_naca('0012')),
                Section((.2, 0, .5), .9, 0, airfoil=Airfoil.from_naca('0012')),
            ],
            origin_position=(3.8, 0, .5),
            y_duplicate=False,
            airfoil=Airfoil.from_naca('0012')
        )
        g = Geometry(
            name="default",
            chord_length=wing.mac(),
            span_length=wing.span,
            surfaces=[wing, h_tail, v_tail],
            surface_area=wing.mac() * wing.span,
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
        path = Path(path)
        with open(path) as f: raw_lines = f.readlines()
        lines = cls.format_lines(raw_lines)
        return cls.handle_top_level(lines, path)

    @classmethod
    def format_lines(cls, raw_lines: list[str]) -> list[str]:
        """Returns a list of lines after formatting."""
        lines = []
        for line in raw_lines:
            if '#' in line:
                line = line.split('#')[0]
            elif '!' in line:
                line = line.split('!')[0]
            elif '|' in line:
                line = line.split('|')[0]
            line = line.strip()
            if not line: continue
            lines.append(line)
        return lines

    @classmethod
    def split_into_blocks(cls, lines: list[str], keywords: tuple[str, ...]) -> list[tuple[str, list[str]]]:
        """Splits lines into blocks, each block starting with one of the given keywords."""
        current_block = None
        blocks = []

        def keyword_in_line(l) -> str | None:
            for kw in keywords:
                if kw[:4] in l: return kw
            return None

        for line in lines:
            keyword = keyword_in_line(line)
            if keyword is not None:
                if current_block is not None: blocks.append(current_block)
                current_block = (keyword, [line])
            else:
                if current_block is None: continue
                current_block[1].append(line)
        if current_block is not None: blocks.append(current_block)
        return blocks

    @classmethod
    def handle_top_level(cls, lines: list[str], path: Path) -> Geometry:
        """Returns a Geometry object based on .avl file."""
        # Reading
        readable = '\n'.join(lines)
        name = lines.pop(0)
        mach = float(lines.pop(0).split()[0])
        syms = tuple(map(float, lines.pop(0).split()[:3]))
        refs = tuple(map(float, lines.pop(0).split()[:3]))
        ref_pos = tuple(map(float, lines.pop(0).split()[:3]))
        next_line = lines.pop(0)
        try:
            CDp = float(next_line.split()[0])
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
        for keyword, lines in blocks:
            if keyword == 'SURFACE':
                geometry_data['surfaces'].append(
                    cls.handle_surface_level(lines[1:], path)
                )
            if keyword == 'BODY': cls.error('GAVL does not support BODY. The block is being skipped.')

        return Geometry(**geometry_data)

    @classmethod
    def handle_surface_level(cls, block: list[str], path: Path) -> Surface:
        """Returns a Surface based on .avl description lines."""
        surface_data: dict[str, Any] = {
            'name': None,
            'sections': [],
            'y_duplicate': False,
            'origin_position': (0, 0, 0),
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
        scale = (1, 1, 1)
        angle = 0
        for keyword, lines in blocks:
            match keyword:
                case kw if kw in ('COMPONENT', 'INDEX'):
                    cls.error(f"{kw}")
                case 'YDUPLICATE':
                    if float(lines[1].split()[0]) == 0.0:
                        surface_data['y_duplicate'] = True
                    else:
                        cls.error(f"YDUPLICATE cannot be non-zero!")  # TODO: fix?
                case 'SCALE':
                    scale = tuple(map(float, lines[1].split()[:3]))
                case 'TRANSLATE':
                    vals = map(float, lines[1].split()[:3])
                    surface_data['origin_position'] = Vector3(*vals)
                case 'ANGLE':
                    angle = float(lines[1].split()[0])
                case kw if kw in ('NOWA', 'NOAL', 'NOLO'):
                    cls.error(f"{kw}")
                case 'CDCL':
                    cls.error("CDCL")
                case 'SECTION':
                    surface_data['sections'].append(
                        cls.handle_section_level(lines[1:], path, scale, angle)
                    )

        surface_data['airfoil'] = surface_data['sections'][0].airfoil
        return SurfaceCreator.UnknownSurface(**surface_data)

    @classmethod
    def handle_section_level(cls, block: list[str], path: Path, scale=(1, 1, 1), angle=0) -> Section:
        """Returns a Section based on .avl description lines."""
        vals = list(map(float, block.pop(0).split()))
        section_data: dict[str, Any] = {
            'leading_edge_position': Vector3(*vals[:3]).scale(scale),
            'chord': vals[3],
            'inclination': vals[4] + angle,
            'airfoil': None,
            'control': None
        }

        blocks = cls.split_into_blocks(block, ('NACA', 'AIRFOIL', 'AFILE', 'CONTROL', 'DESIGN'))
        for keyword, lines in blocks:
            match keyword:
                case 'NACA':
                    section_data['airfoil'] = Airfoil.from_naca(naca=' '.join(lines[1].split()[:2]))
                case 'AIRFOIL':
                    if '#' in lines[0]:
                        name = lines[0].split('#')[1]
                    else:
                        name = 'UnknownAirfoil'
                    lines = lines[1:]
                    points_str = [line.split() for line in lines]
                    points_float = [(float(x), float(y)) for x, y in points_str]
                    section_data['airfoil'] = Airfoil.from_points(name=name, points=points_float)
                case 'AFILE':
                    _path = lines[1]
                    if '"' in _path:
                        start = _path.find('"') + 1
                        end = _path.rfind('"')
                        _path = _path[start:end]
                    else:
                        _path = _path.split()[0]
                    afile_path = Path(_path)
                    if not afile_path.exists():
                        afile_path = path.parent / afile_path
                    section_data['airfoil'] = Airfoil.from_file(afile_path)
                case 'CONTROL':
                    section_data['control'] = cls.handle_control_level(lines[1:])
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
            'instance_name': name,
            'gain': vals[0],
            'x_hinge': vals[1]
        }
        if len(vals) == 6:
            control_data['SgnDup'] = str(vals[5])
        return Control(**control_data)

    @classmethod
    def error(cls, message: str) -> None:
        """Handles a Syntax Error in the .avl file."""
        print(f'Keyword ignored: {message}')  # Temporary

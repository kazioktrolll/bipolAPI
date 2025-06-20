from math import degrees, atan
from typing import Optional

from .horizontal_surface import HorizontalSurface
from ...section import Control
from ...section import Section


class HorizontalSimpleSurface:
    """ A subclass of the ``Surface`` representing a simple, horizontal, trapezoidal lifting surface. """

    @staticmethod
    def from_complex(surface: HorizontalSurface, accuracy=.05, searching=False) -> Optional['HorizontalSurface']:
        root = surface.sections[0]
        tip = surface.sections[-1]

        leading_edge_x_equation = lambda _y: root.x + _y / tip.y * (tip.x - root.x)
        leading_edge_z_equation = lambda _y: root.z + _y / tip.y * (tip.z - root.z)
        chord_equation = lambda _y: root.chord + _y / tip.y * (tip.chord - root.chord)
        inc = root.inclination

        # Check if the surface is of correct shape
        for section in surface.sections:
            y = section.y
            le = section.leading_edge_position
            c = section.chord
            if abs((le.x - leading_edge_x_equation(y)) / c) > accuracy: return None
            if abs((le.z - leading_edge_z_equation(y)) / c) > accuracy: return None
            if abs((c - chord_equation(y)) / c) > accuracy: return None
            if section.inclination != inc: return None

        taper = tip.chord / root.chord
        sweep = degrees(atan(
            (root.get_position_at_xc(.25).x - tip.get_position_at_xc(.25).x) / (tip.y - root.y)
        ))

        simplified = HorizontalSurface.simple_tapered(
            surface.name, surface.span(), surface.mac(), taper, sweep, surface.origin_position, inc, surface.airfoil
        )

        ## Set Mechanization

        # Add the mechanisation
        try:
            controls = HorizontalSimpleSurface._read_controls_from_complex(surface)
            simplified.set_mechanization(**controls)
        except Exception as e:
            if searching:
                return None
            raise e

        return simplified

    @staticmethod
    def _read_controls_from_complex(complex_surf: HorizontalSurface):
        previous_control: Control | None = None
        current_range = [None, None]
        ranges: dict[str, list[tuple[float, float, float]]] = {}

        def start_block(s: Section) -> tuple[Control, list[int]]:
            return s.control, [s.y, None]

        def break_block():
            # If the previous control is None, there is no block to break.
            if previous_control is None: return
            # If this is the first block of this type, create a list for it.
            name = previous_control.name
            if name not in ranges.keys(): ranges[name] = []
            # Append the dict by this block.
            if None in current_range: raise ValueError
            ranges[name].append((current_range[0], current_range[1], previous_control.x_hinge))  # noqa

        for section in complex_surf.sections:
            # If this section has the same control as the previous, extend block and continue.
            if section.control and section.control.is_equal_to(previous_control):
                current_range[1] = section.y
                continue
            # Now we know that the block needs to be broken
            break_block()

            # If this section has a new control, start a new block
            if section.control is not None:
                previous_control, current_range = start_block(section)
        # Break the last block
        break_block()

        return ranges

from typing import Literal

from .surface import Surface


class HorizontalSurface(Surface):

    def get_type(self, accuracy=0.05) -> None | Literal['Rectangular', 'Delta', 'Simple Tapered', 'Double Trapez']:
        if HorizontalSurface.is_delta(self, accuracy):
            return 'Delta'
        tapered = HorizontalSurface.is_simple_tapered(self, accuracy)
        # double_trapez = HorizontalSurface.is_double_trapez(self, accuracy)
        double_trapez = False

        if tapered and self.taper_ratio() == 1 and self.sweep_angle() == 0: return 'Rectangular'
        if tapered: return 'Simple Tapered'
        if double_trapez: return 'Double Trapez'
        return None

    @classmethod
    def is_delta(cls, surface: 'HorizontalSurface', accuracy=.05) -> bool:
        if not cls.is_simple_tapered(surface, accuracy):
            return False
        root = surface.sections[0]
        tip = surface.sections[-1]
        if tip.chord != 0: return False
        if not tip.trailing_edge_position == root.trailing_edge_position: return False
        return True

    @staticmethod
    def is_double_trapez(surface: 'HorizontalSurface', accuracy=.05) -> bool:
        raise NotImplementedError

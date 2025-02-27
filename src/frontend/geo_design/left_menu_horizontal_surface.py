from .left_menu_item import LeftMenuItem
from ...backend.geo_design import HorizontalSurface


class LeftMenuHorizontalSurface(LeftMenuItem):
    def __init__(self, parent, surface: HorizontalSurface):
        super().__init__(parent, surface)

    def init_pfs(self) -> None:
        # keyword, name, message, assert, initial
        HorizontalSurface()
        pfs_params = [
            ('chord', 'MAC'),
            ('sections'),
            ('y_duplicate'),
            ('x'),
            ('y'),
            ('z')
        ]

from .left_menu_item import LeftMenuItem, LMOblique, LMEmpty
from .left_menu_items_horizontal import LMTapered, LMRectangular, LMDelta, LMDoubleTrapez
from .left_menu_items_vertical import LMRectangularV, LMSimpleTaperedV, LMTwinV
from ....backend.geo_design import Surface, HorizontalSurface, Geometry, VerticalSurface
from ....backend import handle_crash
from customtkinter import CTkFrame, CTkOptionMenu


class LeftMenuSurface(CTkFrame):
    @handle_crash
    def __init__(self, parent: CTkFrame, surface: Surface, types: dict[str, type[LeftMenuItem]]):
        super().__init__(parent)
        self.name = surface.name
        self.types = types
        self.option_menu = CTkOptionMenu(
            self, values=list(types.keys()), command=lambda t: self.set_lm(types[t])
        )
        self.option_menu.grid(row=0, column=0, sticky='nsew')
        self.lm: LeftMenuItem = LMEmpty(self, surface)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.auto_set(surface)

    @handle_crash
    def set_lm(self, lm: type[LeftMenuItem]) -> None:
        self.option_menu.set(self.get_name_from_type(lm))
        _lm = lm(self, self.surface)
        self.lm.grid_forget()
        _lm.grid(row=1, column=0, sticky='nsew')
        self.lm = _lm
        _lm.update_surface()

    def get_name_from_type(self, _lm: type[LeftMenuItem]) -> str | None:
        for n, t in self.types.items():
            if _lm == t:
                return n
        return None

    def auto_set(self, surface: HorizontalSurface | VerticalSurface) -> None:
        _t = surface.get_type()
        if _t is None:
            raise TypeError
        self.set_lm(self.types[str(_t)])

    @property
    def geometry(self) -> Geometry:
        from .left_menu import LeftMenu
        assert isinstance(self.master, LeftMenu)
        return self.master.geometry

    @property
    def surface(self) -> Surface:
        return self.geometry.surfaces[self.name]


class LeftMenuHorizontal(LeftMenuSurface):
    @handle_crash
    def __init__(self, parent: CTkFrame, surface: Surface):
        types = {
            'Rectangular': LMRectangular,
            'Simple Tapered': LMTapered,
            'Double Trapez': LMDoubleTrapez,
            'Delta': LMDelta,
            'None': LMEmpty,
        }
        if surface.name == 'Wing':
            del types['None']
        super().__init__(parent=parent, surface=surface, types=types)



class LeftMenuVertical(LeftMenuSurface):
    @handle_crash
    def __init__(self, parent: CTkFrame, surface: Surface):
        types = {
            'Rectangular': LMRectangularV,
            'Simple Tapered': LMSimpleTaperedV,
            'Twin': LMTwinV,
            'None': LMEmpty,
        }
        super().__init__(parent=parent, surface=surface, types=types)


class LeftMenuOblique(LeftMenuSurface):
    @handle_crash
    def __init__(self, parent: CTkFrame, surface: Surface):
        types = {'Oblique': LMOblique}
        super().__init__(parent=parent, surface=surface, types=types)
        self.set_lm(LMOblique)

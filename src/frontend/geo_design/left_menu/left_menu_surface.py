from .left_menu_item import LeftMenuItem, LMOblique, LMEmpty
from .left_menu_items_horizontal import LMTapered, LMRectangular, LMDelta
from ....backend.geo_design import Surface, HorizontalSurface, Geometry
from customtkinter import CTkFrame, CTkOptionMenu


class LeftMenuSurface(CTkFrame):
    def __init__(self, parent: CTkFrame, surface: Surface, types: dict[str, type[LeftMenuItem]]):
        super().__init__(parent)
        self.name = surface.name
        self.option_menu = CTkOptionMenu(
            self, values=list(types.keys()), command=lambda t: self.set_lm(types[t])
        )
        self.option_menu.grid(row=0, column=0, sticky='nsew')
        self.lm: LeftMenuItem = LMEmpty(self, surface)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.set_lm(LMEmpty)

    def set_lm(self, lm: type[LeftMenuItem]) -> None:
        _lm = lm(self, self.surface)
        self.lm.grid_forget()
        _lm.grid(row=1, column=0, sticky='nsew')
        self.lm = _lm
        _lm.update_surface()

    @property
    def geometry(self) -> Geometry:
        from .left_menu import LeftMenu
        assert isinstance(self.master, LeftMenu)
        return self.master.geometry

    @property
    def surface(self) -> Surface:
        return self.geometry.surfaces[self.name]


class LeftMenuHorizontal(LeftMenuSurface):
    def __init__(self, parent: CTkFrame, surface: Surface):
        types = {
            'Rectangular': LMRectangular,
            'Simple Tapered': LMTapered,
            'Double Trapez': ...,
            'Delta': LMDelta,
            'V-Shape': ...,
            'Canard': ...,
            'None': ...,
        }
        if surface.name == 'Wing':
            del types['V-Shape']
            del types['Canard']
            del types['None']
        elif surface.name == 'H Tail':
            del types['Double Trapez']
            del types['Delta']
        super().__init__(parent=parent, surface=surface, types=types)
        assert isinstance(surface, HorizontalSurface)
        _t = surface.get_type()
        if _t is None:
            raise TypeError
        self.set_lm(types[str(_t)])


class LeftMenuVertical(LeftMenuSurface):
    def __init__(self, parent: CTkFrame, surface: Surface):
        types = {
            'Rectangular': ...,
            'Simple Tapered': ...,
            'Twin': ...,
            'None': ...,
        }
        super().__init__(parent=parent, surface=surface, types=types)


class LeftMenuOblique(LeftMenuSurface):
    def __init__(self, parent: CTkFrame, surface: Surface):
        types = {'Oblique': LMOblique}
        super().__init__(parent=parent, surface=surface, types=types)
        self.set_lm(LMOblique)

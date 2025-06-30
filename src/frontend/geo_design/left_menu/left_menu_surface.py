from .left_menu_item import LeftMenuItem, LMOblique, LMEmpty
from .left_menu_items_horizontal import LMTapered, LMRectangular, LMDelta, LMDoubleTrapez
from .left_menu_items_vertical import LMRectangularV, LMSimpleTaperedV
from ....backend.geo_design import Surface, Geometry
from ....backend import handle_crash
from customtkinter import CTkFrame, CTkOptionMenu


class LeftMenuSurface(CTkFrame):
    @handle_crash
    def __init__(self, parent: CTkFrame, surface: Surface):
        super().__init__(parent)
        self.name = surface.name

        self.types: dict[str, type[LeftMenuItem]] = {
            'Rectangular': LMRectangular,
            'Simple Tapered': LMTapered,
            'Double Trapez': LMDoubleTrapez,
            'Delta': LMDelta,
            'Vertical Rectangular': LMRectangularV,
            'Vertical Tapered': LMSimpleTaperedV,
            'Oblique': LMOblique,
            'None': LMEmpty,
        }
        self.option_menu = CTkOptionMenu(
            self, values=list(self.types.keys()), command=lambda t: self.set_lm(self.types[t])
        )
        self.lm: LeftMenuItem = LMEmpty(self, surface)
        self.auto_set(surface)

        if surface.name == 'Wing':
            del self.types['None']
            del self.types['Vertical Rectangular']
            del self.types['Vertical Tapered']
        if surface.name == 'H Tail':
            del self.types['Vertical Rectangular']
            del self.types['Vertical Tapered']
        if surface.name == 'V Tail':
            del self.types['Rectangular']
            del self.types['Delta']
            del self.types['Double Trapez']
        del self.types['Oblique']

        self.option_menu.configure(values=list(self.types.keys()))
        self.option_menu.grid(row=0, column=0, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

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

    def auto_set(self, surface: Surface) -> None:
        _t = surface.template.get_type(surface)
        if _t is None:
            self.set_lm(LMOblique)
        else:
            self.set_lm(self.types[str(_t)])

    @property
    def geometry(self) -> Geometry:
        from .left_menu import LeftMenu
        assert isinstance(self.master, LeftMenu)
        return self.master.geometry

    @property
    def surface(self) -> Surface:
        return self.geometry.surfaces[self.name]

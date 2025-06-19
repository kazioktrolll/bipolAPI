from .left_menu_item import LeftMenuItem
from ....backend.geo_design import Surface
from customtkinter import CTkFrame, CTkOptionMenu
from typing import Callable


LM_maker = Callable[[CTkFrame, Surface], LeftMenuItem]


class LeftMenuSurface(CTkFrame):
    def __init__(self, parent: CTkFrame, surface: Surface, types: dict[str, LM_maker]):
        super().__init__(parent)
        self.surface = surface
        self.option_menu = CTkOptionMenu(
            self, values=list(types.keys()), command=lambda t: self.set_lm(types[t](self, surface))
        )
        self.option_menu.grid(row=0, column=0, sticky='nsew')
        self.lm: LeftMenuItem = None    # TODO finish
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def set_lm(self, lm: LeftMenuItem) -> None:
        self.lm.grid_forget()
        lm.grid(row=1, column=0, sticky='nsew')
        self.lm = lm

    @property
    def name(self) -> str:
        return self.surface.name


class LeftMenuHorizontal(LeftMenuSurface):
    def __init__(self, parent: CTkFrame, surface: Surface):
        types = {
            'Rectangular': ...,
            'Simple Tapered': ...,
            'Double Trapez': ...,
            'Delta': ...,
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
        types = {'Oblique': ...}
        super().__init__(parent=parent, surface=surface, types=types)

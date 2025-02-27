from customtkinter import CTkFrame, CTkButton, ThemeManager
from typing import Callable

from .left_menu_simple_surface import LeftMenuSimpleSurface
from .left_menu_vertical_surface import LeftMenuVerticalSurface
from ...backend.geo_design import Geometry


class LeftMenu(CTkFrame):
    def __init__(self, parent, do_on_update: Callable[[], None]):
        super().__init__(parent)

        self._do_on_update = do_on_update

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.buttons = CTkFrame(self, fg_color=self.cget("fg_color"))
        self.buttons.columnconfigure(0, weight=1)
        self.buttons.columnconfigure(1, weight=1)
        self.buttons.columnconfigure(2, weight=1)
        self.buttons.rowconfigure(0, minsize=4)
        self.buttons.grid(row=0, column=0, sticky='nsew')
        CTkButton(self.buttons, text="Wing", command=self.show_wing, width=50
                  ).grid(row=1, column=0, sticky='nsew')
        CTkButton(self.buttons, text="Ver. Tail", command=self.show_v_tail, width=50
                  ).grid(row=1, column=1, sticky='nsew', padx=5)
        CTkButton(self.buttons, text="Hor. Tail", command=self.show_h_tail, width=50
                  ).grid(row=1, column=2, sticky='nsew')

        self.rowconfigure(1, minsize=4)

        self.wing = LeftMenuSimpleSurface.default(self, 'wing')
        self.v_tail = LeftMenuVerticalSurface.default(self, 'v_tail')
        self.h_tail = LeftMenuSimpleSurface.default(self, 'h_tail')

        self.show_wing()

    @property
    def geometry(self) -> Geometry:
        from ...scenes import GeoDesignScene
        assert isinstance(self.master, GeoDesignScene)
        return self.master.geometry

    def do_on_update(self) -> None:
        self._do_on_update()

    def show_wing(self):
        if self.wing.grid_info() != {}: return
        self.v_tail.place(x=-1e4, y=-1e4)
        self.h_tail.place(x=-2e4, y=-2e4)
        self.wing.grid(row=2, column=0, sticky='nsew', padx=10)
        self.wing_button.configure(fg_color=ThemeManager.theme["CTkButton"]["fg_color"], state="enabled")   # noqa
        self.v_tail_button.configure(fg_color=ThemeManager.theme["CTkFrame"]["fg_color"], state="normal")   # noqa
        self.h_tail_button.configure(fg_color=ThemeManager.theme["CTkFrame"]["fg_color"], state="normal")   # noqa

    def show_v_tail(self):
        if self.v_tail.grid_info() != {}: return
        self.wing.place(x=-1e4, y=-1e4)
        self.h_tail.place(x=-2e4, y=-2e4)
        self.v_tail.grid(row=2, column=0, sticky='nsew', padx=10)
        self.wing_button.configure(fg_color=ThemeManager.theme["CTkFrame"]["fg_color"], state="normal")   # noqa
        self.v_tail_button.configure(fg_color=ThemeManager.theme["CTkButton"]["fg_color"], state="enabled")   # noqa
        self.h_tail_button.configure(fg_color=ThemeManager.theme["CTkFrame"]["fg_color"], state="normal")   # noqa

    def show_h_tail(self):
        if self.h_tail.grid_info() != {}: return
        self.wing.place(x=-1e4, y=-1e4)
        self.v_tail.place(x=-2e4, y=-2e4)
        self.h_tail.grid(row=2, column=0, sticky='nsew', padx=10)
        self.wing_button.configure(fg_color=ThemeManager.theme["CTkFrame"]["fg_color"], state="normal")  # noqa
        self.v_tail_button.configure(fg_color=ThemeManager.theme["CTkFrame"]["fg_color"], state="normal")  # noqa
        self.h_tail_button.configure(fg_color=ThemeManager.theme["CTkButton"]["fg_color"], state="enabled")  # noqa

    @property
    def wing_button(self):
        return self.buttons.children['!ctkbutton']   # noqa

    @property
    def v_tail_button(self):
        return self.buttons.children['!ctkbutton2']   # noqa

    @property
    def h_tail_button(self):
        return self.buttons.children['!ctkbutton3']   # noqa
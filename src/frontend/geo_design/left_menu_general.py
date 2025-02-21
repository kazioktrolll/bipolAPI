from customtkinter import CTkFrame, CTkButton, ThemeManager
from typing import Callable

from .left_menu_wing import LeftMenuWing
from ...backend.geo_design import Geometry


class LeftMenu(CTkFrame):
    def __init__(self, parent, geometry: Geometry, do_on_update: Callable[[], None]):
        super().__init__(parent)

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

        self.wing = LeftMenuWing(self, geometry, do_on_update)


        self.show_wing()

    def show_wing(self):
        self.wing.grid(row=2, column=0, sticky='nsew', padx=10)
        self.wing_button.configure(fg_color=ThemeManager.theme["CTkButton"]["fg_color"], state="enabled")   # noqa
        self.v_tail_button.configure(fg_color=ThemeManager.theme["CTkFrame"]["fg_color"], state="normal")   # noqa
        self.h_tail_button.configure(fg_color=ThemeManager.theme["CTkFrame"]["fg_color"], state="normal")   # noqa

    def show_v_tail(self):
        pass

    def show_h_tail(self):
        pass

    @property
    def wing_button(self):
        return self.buttons.children['!ctkbutton']   # noqa

    @property
    def v_tail_button(self):
        return self.buttons.children['!ctkbutton2']   # noqa

    @property
    def h_tail_button(self):
        return self.buttons.children['!ctkbutton3']   # noqa
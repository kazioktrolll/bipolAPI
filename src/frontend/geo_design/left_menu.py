from customtkinter import CTkFrame, CTkButton, ThemeManager
from typing import Callable

from .left_menu_item import LeftMenuItem
from .left_menu_simple_surface import LeftMenuSimpleSurface
from .left_menu_vertical_surface import LeftMenuVerticalSurface
from ...backend.geo_design import Geometry, SimpleSurface, VerticalSurface


class LeftMenu(CTkFrame):
    def __init__(self, parent, do_on_update: Callable[[], None]):
        super().__init__(parent)

        self._do_on_update = do_on_update
        self.items: dict[str, LeftMenuItem] = {}
        self.buttons: dict[str, CTkButton] = {}
        self.buttons_frame = CTkFrame(self, fg_color=self.cget("fg_color"))

        self.update_items()
        self.build()
        self.show_first()

    def build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.buttons_frame.grid(row=0, column=0, sticky='nsew')
        self.buttons_frame.children.clear()

        for i, (name, item) in enumerate(self.items.items()):
            self.buttons[name] = CTkButton(self.buttons_frame, text=name, width=40, command=lambda: self.show_item(name))
            self.buttons[name].grid(row=1, column=i, sticky="nsew")
            self.buttons_frame.columnconfigure(i, weight=1)

        self.rowconfigure(1, minsize=4)

    def update_items(self) -> None:
        menu_item = {SimpleSurface: LeftMenuSimpleSurface,
                     VerticalSurface: LeftMenuVerticalSurface}
        for name, surface in self.geometry.surfaces.items():
            self.items[name] = menu_item[type(surface)](self, surface)

    @property
    def geometry(self) -> Geometry:
        from ...scenes import GeoDesignScene
        assert isinstance(self.master, GeoDesignScene)
        return self.master.geometry

    def do_on_update(self) -> None:
        self._do_on_update()

    def show_item(self, item: str) -> None:
        if self.items[item].grid_info() != {}: return

        for i, name in enumerate(self.items.keys()):
            if name == item:
                self.items[name].grid(row=2, column=0, sticky='nsew', padx=10)
                self.buttons[name].configure(fg_color=ThemeManager.theme["CTkButton"]["fg_color"], state="enabled") # noqa
                continue
            self.items[name].place(x=-i*1e4, y=-1e4)
            self.buttons[name].configure(fg_color=ThemeManager.theme["CTkFrame"]["fg_color"], state="normal")       # noqa

    def show_first(self) -> None:
        first = tuple(self.items.keys())[-1]
        self.show_item(first)

    @property
    def wing_button(self):
        return self.buttons.children['!ctkbutton']   # noqa

    @property
    def v_tail_button(self):
        return self.buttons.children['!ctkbutton2']   # noqa

    @property
    def h_tail_button(self):
        return self.buttons.children['!ctkbutton3']   # noqa
from customtkinter import CTkFrame, CTkButton, ThemeManager
from typing import Callable

from .left_menu_item import LeftMenuItem, LeftMenuNotImplemented
from .left_menu_simple_surface import LeftMenuSimpleSurface
from .left_menu_vertical_surface import LeftMenuVerticalSurface
from ...backend.geo_design import Geometry, SimpleSurface, VerticalSurface, HorizontalSurface


class LeftMenu(CTkFrame):
    def __init__(self, parent, do_on_update: Callable[[], None]):
        super().__init__(parent)

        self._do_on_update = do_on_update
        self.items: list[LeftMenuItem] = []
        self.buttons_frame = CTkFrame(self, fg_color=self.cget("fg_color"))

        self.update_items()
        self.build()
        self.show_first()

    def build(self) -> None:
        self.columnconfigure(0, weight=1)

        self.buttons_frame.grid(row=0, column=0, sticky='nsew')
        self.rowconfigure(1, minsize=4)
        self.rowconfigure(2, weight=1)

        self.buttons_frame.children.clear()

        for i, item in enumerate(self.items):
            item.button.grid(row=1, column=i, sticky="nsew")
            self.buttons_frame.columnconfigure(i, weight=1)

    def update_items(self) -> None:
        menu_item = {SimpleSurface: LeftMenuSimpleSurface,
                     VerticalSurface: LeftMenuVerticalSurface,
                     HorizontalSurface: LeftMenuNotImplemented}
        for name, surface in self.geometry.surfaces.items():
            item_type = menu_item[type(surface)]
            self.items.append(item_type(self, surface))

    @property
    def geometry(self) -> Geometry:
        from ...scenes import GeoDesignScene
        assert isinstance(self.master, GeoDesignScene)
        return self.master.geometry

    def do_on_update(self) -> None:
        self._do_on_update()

    def show_item(self, clicked: LeftMenuItem) -> None:
        if clicked.grid_info() != {}: return

        for i, item in enumerate(self.items):
            if item == clicked:
                item.grid(row=2, column=0, sticky='nsew', padx=10)
                item.button.configure(fg_color=ThemeManager.theme["CTkButton"]["fg_color"], state="enabled") # noqa
                continue
            item.place(x=-i*1e4, y=-1e4)
            item.button.configure(fg_color=ThemeManager.theme["CTkFrame"]["fg_color"], state="normal")       # noqa

    def show_first(self) -> None:
        self.show_item(self.items[0])

from customtkinter import CTkFrame, ThemeManager, CTkSegmentedButton
from typing import Callable

from .left_menu_item import LeftMenuItem
from .left_menu_simple_surface import LeftMenuSimpleSurface
from .left_menu_vertical_surface import LeftMenuVerticalSurface
from .left_menu_horizontal_surface import LeftMenuHorizontalSurface
from ...backend.geo_design import Geometry, HorizontalSimpleSurface, VerticalSimpleSurface, HorizontalSurface


class LeftMenu(CTkFrame):
    def __init__(self, parent, do_on_update: Callable[[], None]):
        super().__init__(parent)

        self._do_on_update = do_on_update
        self.items: dict[str, LeftMenuItem] = {}
        self.items_button = CTkSegmentedButton(self, command=lambda c: self.show_item(name=c))

        self.update_items()
        self.build()
        self.show_first()

    def build(self) -> None:
        self.columnconfigure(0, weight=1)

        self.items_button.grid(row=0, column=0, sticky='nsew')
        self.rowconfigure(1, minsize=4)
        self.rowconfigure(2, weight=1)

    def update(self) -> None:
        self.update_items()
        self.build()
        self.show_first()

    def update_items(self) -> None:
        menu_item = {HorizontalSimpleSurface: LeftMenuSimpleSurface,
                     VerticalSimpleSurface: LeftMenuVerticalSurface,
                     HorizontalSurface: LeftMenuHorizontalSurface}
        self.items.clear()
        for name, surface in self.geometry.surfaces.items():
            item_type = menu_item[type(surface)]
            self.items[name] = item_type(self, surface)
        self.items_button.configure(values=[item.name for item in self.items.values()])

    @property
    def geometry(self) -> Geometry:
        from ...scenes import GeoDesignScene
        assert isinstance(self.master, GeoDesignScene)
        return self.master.geometry

    def do_on_update(self) -> None:
        self._do_on_update()

    def show_item(self, clicked: LeftMenuItem = None, name: str = None) -> None:
        clicked = clicked or self.items[name]

        for i, item in enumerate(self.items.values()):
            if item == clicked:
                item.grid(row=2, column=0, sticky='nsew', padx=10)
                continue
            item.place(x=-i*1e4, y=-1e4)

    def show_first(self) -> None:
        if len(self.items) > 0:
            self.show_item(clicked=list(self.items.values())[0])

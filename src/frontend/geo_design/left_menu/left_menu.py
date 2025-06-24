"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkSegmentedButton
from typing import Callable

from .left_menu_surface import LeftMenuSurface, LeftMenuHorizontal, LeftMenuVertical, LeftMenuOblique
from ....backend.geo_design import Geometry, HorizontalSurface, VerticalSurface
from ....backend import handle_crash


class LeftMenu(CTkFrame):
    def __init__(self, parent, do_on_update: Callable[[], None]):
        super().__init__(parent)

        self._do_on_update = do_on_update
        self.items: dict[str, LeftMenuSurface] = {}
        self.items_button = CTkSegmentedButton(self, command=lambda c: self.show_item(name=c))

        self.update_items()
        self.build()
        self.show_first()

    def build(self) -> None:
        self.columnconfigure(0, weight=1)

        self.items_button.grid(row=0, column=0, sticky='nsew')
        self.rowconfigure(1, minsize=4)
        self.rowconfigure(2, weight=1)

    @handle_crash
    def update(self) -> None:
        self.update_items()
        self.build()
        self.show_first()

    def update_items(self) -> None:
        menu_item = {HorizontalSurface: LeftMenuHorizontal,
                     VerticalSurface: LeftMenuVertical}
        self.items.clear()
        for name, surface in self.geometry.surfaces.items():
            try:
                item_type = menu_item[type(surface)]
            except KeyError:
                item_type = LeftMenuOblique
            self.items[name] = item_type(self, surface)
        self.items_button.configure(values=[item.name for item in self.items.values()])

    @property
    def geometry(self) -> Geometry:
        from ....scenes import GeoDesignScene
        assert isinstance(self.master, GeoDesignScene)
        return self.master.geometry

    @handle_crash
    def do_on_update(self) -> None:
        self._do_on_update()

    def show_item(self, clicked: LeftMenuSurface = None, name: str = None) -> None:
        clicked = clicked or self.items[name]

        for i, item in enumerate(self.items.values()):
            if item == clicked:
                item.grid(row=2, column=0, sticky='nsew', padx=10)
                continue
            item.place(x=-i * 1e4, y=-1e4)

    def show_first(self) -> None:
        if len(self.items) > 0:
            first = list(self.items.values())[0]
            self.show_item(clicked=first)
            self.items_button.set(first.name)

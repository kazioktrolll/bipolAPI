"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkSegmentedButton, CTkButton, CTkLabel
from typing import Callable
from pathlib import Path

from .left_menu_surface import LeftMenuSurface
from ....backend.geo_design import Geometry
from ....backend import handle_crash


class LeftMenu(CTkFrame):
    def __init__(self, parent, do_on_update: Callable[[], None], recently_saved: list[Path] = None):
        super().__init__(parent)

        self._do_on_update = do_on_update
        self.items: dict[str, LeftMenuSurface] = {}
        self.items_button = CTkSegmentedButton(self, command=lambda c: self.show_item(name=c))
        # Create Init Menu
        self.empty_menu_buttons = CTkFrame(self, fg_color='transparent')
        self.empty_menu_buttons.columnconfigure(0, weight=1)
        if recently_saved:
            CTkLabel(self.empty_menu_buttons, text='\tRecent:'
                     ).grid(column=0, row=0, sticky='w', padx=5, pady=5)
            for i, path in enumerate(recently_saved):
                CTkButton(self.empty_menu_buttons, text=path.name, command=lambda p=path: self.app.load(p), width=250
                          ).grid(column=0, row=i + 1, sticky='w', padx=5, pady=5)
        CTkButton(self.empty_menu_buttons, text='Open', command=self.app.load
                  ).grid(column=0, row=6, sticky='nswe', padx=5, pady=5)
        CTkButton(self.empty_menu_buttons, text='New', command=self.app.new_default
                  ).grid(column=0, row=7, sticky='nswe', padx=5, pady=5)
        CTkButton(self.empty_menu_buttons, text='Import', command=self.app.import_from_avl
                  ).grid(column=0, row=8, sticky='nswe', padx=5, pady=5)

        self.build()
        self.update()
        self.show_first()

    def build(self) -> None:
        self.columnconfigure(0, weight=1, minsize=450)

        self.items_button.grid(row=0, column=0, sticky='nsew')
        self.rowconfigure(1, minsize=4)
        self.rowconfigure(2, weight=1)

    @handle_crash
    def update(self) -> None:
        self.update_items()
        self.update_empty_buttons()
        self.show_first()

    def update_items(self) -> None:
        self.items.clear()
        for name, surface in self.geometry.surfaces.items():
            self.items[name] = LeftMenuSurface(self, surface)
        self.items_button.configure(values=[item.name for item in self.items.values()])

    @property
    def geometry(self) -> Geometry:
        from ....scenes import GeoDesignScene
        assert isinstance(self.master, GeoDesignScene)
        return self.master.geometry

    @property
    def app(self):
        from ....scenes import GeoDesignScene
        assert isinstance(self.master, GeoDesignScene)
        return self.master.app

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

    def update_empty_buttons(self):
        if len(self.items.values()) > 0:
            self.empty_menu_buttons.grid_forget()
        else:
            self.empty_menu_buttons.grid(row=1, column=0, sticky='nsew')

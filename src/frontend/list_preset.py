"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from typing import Callable
from customtkinter import CTkFrame, CTkLabel, CTkButton
from .items import Item
from ..backend import handle_crash


class ListPreset:
    def __init__(self, parent, category_name: str, item_class: type[Item], do_on_update: Callable[[], None]) -> None:
        self.category_name = category_name
        self.item_class = item_class
        self.do_on_update = do_on_update
        self.items: list[Item] = []
        self.item_frames: list[ItemFrame] = []

        self.main_frame = CTkFrame(None)
        self.header_frame = CTkFrame(None)
        self.body_frame = CTkFrame(None)
        self.init_display(parent)

    def init_display(self, parent) -> None:
        self.main_frame = CTkFrame(parent, border_width=3, border_color='gray40')
        self.header_frame = CTkFrame(self.main_frame, fg_color='transparent')
        self.body_frame = CTkFrame(self.main_frame)
        self.main_frame.columnconfigure(0, weight=1)

        self.header_frame.grid(column=0, row=0, padx=5, pady=5, sticky="new")
        self.header_frame.columnconfigure(1, weight=1)
        CTkLabel(self.header_frame, text=self.category_name).grid(column=0, row=0, sticky="w", padx=5, pady=5)
        CTkButton(self.header_frame, text='+', fg_color='green', hover_color='dark green', width=25, height=25,
                  command=self.add_position
                  ).grid(column=1, row=0, sticky="e", padx=5, pady=5)

        self.body_frame.configure(height=0)
        self.body_frame.grid(column=0, row=1, sticky="sew", padx=5, pady=5)
        self.body_frame.columnconfigure(0, weight=1)
        self.redo_item_frames()

    def redo_item_frames(self):
        for frame in self.item_frames: frame.destroy()
        self.item_frames.clear()
        for i, item in enumerate(self.items):
            edit_item = lambda: item.edit(self.do_on_update)
            position = ItemFrame(self, self.body_frame, item, edit_item)
            self.item_frames.append(position)
            position.grid(column=0, row=len(self.body_frame.children) - 1, sticky="nsew")

    def grid(self, **kwargs) -> None:
        self.main_frame.grid(**kwargs)

    def grid_forget(self) -> None:
        self.main_frame.grid_forget()

    def grid_info(self):
        return self.main_frame.grid_info()

    def update_items(self) -> None:
        self.redo_item_frames()
        for i, item_frame in enumerate(self.item_frames):
            item_frame.update()
            item_frame.grid_forget()
            item_frame.grid(column=0, row=i, sticky="nsew")

    @handle_crash
    def add_position(self, item: Item = None) -> None:
        needs_init = item is None
        item = item or self.item_class()
        self.items.append(item)

        edit_item = lambda: item.edit(self.do_on_update)
        position = ItemFrame(self, self.body_frame, item, edit_item)
        self.item_frames.append(position)
        self.update_items()

        if needs_init: edit_item()

    def get_values(self) -> list  :
        return [item.get_values() for item in self.items]


class ItemFrame(CTkFrame):
    def __init__(self, parent: ListPreset, frame: CTkFrame, item: Item, edit_item: Callable[[], None]) -> None:
        super().__init__(frame, border_width=2, border_color='gray30')
        self.item = item
        self.locked = False
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, minsize=35)
        self.columnconfigure(2, minsize=35)

        display = item.display(self)
        display.grid(column=0, row=0, sticky='nswe', padx=5, pady=5)
        CTkButton(self, text='E', width=25, height=25,
                  command=edit_item
                  ).grid(column=1, row=0, sticky="e", padx=5, pady=5)
        self.remove_button = CTkButton(
            self, text='-', fg_color='red3', hover_color='red4', width=25, height=25,
            command=lambda: (self.destroy(), parent.items.remove(item), parent.do_on_update())
        )
        self.update()

    def update(self) -> None:
        if self.locked:
            self.remove_button.grid_forget()
        else:
            self.remove_button.grid(column=2, row=0, sticky="e", padx=5, pady=5)

from typing import Callable

from customtkinter import CTkFrame, CTkLabel, CTkButton
from .items import Item


class ListPreset(CTkFrame):
    def __init__(self, parent, category_name: str, item_class: type[Item], do_on_update: Callable[[], None]) -> None:
        super().__init__(parent)
        self.category_name = category_name
        self.item_class = item_class
        self.do_on_update = do_on_update
        self.items: list[Item] = []
        self.item_frames: list[ItemFrame] = []

        self.header_frame = CTkFrame(self)
        self.body_frame = CTkFrame(self)
        self.init_display()

    def init_display(self) -> None:
        self.columnconfigure(0, weight=1)

        self.header_frame.configure(fg_color=self.cget('fg_color'))
        self.header_frame.grid(column=0, row=0, sticky="new")
        self.header_frame.columnconfigure(1, weight=1)
        CTkLabel(self.header_frame, text=self.category_name).grid(column=0, row=0, sticky="w", padx=5, pady=5)
        CTkButton(self.header_frame, text='+', fg_color='green', hover_color='dark green', width=25, height=25,
                  command=self.add_position
                  ).grid(column=1, row=0, sticky="e", padx=5, pady=5)

        self.body_frame.configure(height=0)
        self.body_frame.grid(column=0, row=1, sticky="sew", padx=5, pady=5)
        self.body_frame.columnconfigure(0, weight=1)

    def update_items(self) -> None:

        for item_frame in self.item_frames: item_frame.update()

    def add_position(self, item: Item = None) -> None:
        needs_init = item is None
        item = item or self.item_class()
        self.items.append(item)

        edit_item = lambda: item.edit(lambda: (display.update(), self.do_on_update())) # noqa
        position = ItemFrame(self, item, edit_item)
        self.item_frames.append(position)
        position.grid(column=0, row=len(self.body_frame.children)-1, sticky="nsew")

        if needs_init: edit_item()

    def get_values(self) -> list[tuple]:
        return [item.get_values() for item in self.items]


class ItemFrame(CTkFrame):
    def __init__(self, parent, item:Item, edit_item: Callable[[], None]) -> None:
        super().__init__(parent)
        self.item = item
        self.locked = False
        self.columnconfigure(0, weight=1)

        display = item.display(self)
        display.grid(column=0, row=0, sticky='nsw', padx=5, pady=5)
        CTkButton(self, text='E', width=25, height=25,
                  command=edit_item
                  ).grid(column=1, row=0, sticky="e", padx=5, pady=5)
        self.remove_button = CTkButton(
            self, text='-', fg_color='red3', hover_color='red4', width=25, height=25,
            command=lambda: (self.destroy(), parent.items.remove(item), parent.do_on_update())
            )
        self.update()

    def update(self) -> None:
        if self.locked: self.remove_button.grid_forget()
        else: self.remove_button.grid(column=2, row=0, sticky="e", padx=5, pady=5)

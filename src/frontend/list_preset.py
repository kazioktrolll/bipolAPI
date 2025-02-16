from typing import Callable

from customtkinter import CTkFrame, CTkLabel, CTkButton
from .items import Item


class ListPreset(CTkFrame):
    def __init__(self, parent, category_name: str, item_class: type[Item], do_on_update: Callable[[], None]) -> None:
        CTkFrame.__init__(self, parent)
        self.category_name = category_name
        self.item_class = item_class
        self.do_on_update = do_on_update
        self.items = []

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

    def add_position(self) -> None:
        position = CTkFrame(self.body_frame, fg_color=self.body_frame.cget('fg_color'))
        position.grid(column=0, row=len(self.body_frame.children)-1, sticky="nsew")
        position.columnconfigure(0, weight=1)

        item = self.item_class()
        self.items.append(item)

        display = item.display(position)
        display.grid(column=0, row=0, sticky='nsw', padx=5, pady=5)
        CTkButton(position, text='E', width=25, height=25,
                  command=lambda: (item.edit(lambda: (display.update(), self.do_on_update())))  # noqa
                  ).grid(column=1, row=0, sticky="e", padx=5, pady=5)
        CTkButton(position, text='-', fg_color='red3', hover_color='red4', width=25, height=25,
                  command=lambda: (position.destroy(), self.items.remove(item), self.do_on_update())
                  ).grid(column=2, row=0, sticky="e", padx=5, pady=5)

    def get_values(self) -> list[tuple]:
        return [item.get_values() for item in self.items]

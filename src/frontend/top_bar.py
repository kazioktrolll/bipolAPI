"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkButton
from typing import Callable


class TopBarItem(CTkButton):
    def __init__(self, parent, root, name: str, options: list[tuple[str, Callable[[], None]]]):
        self.options = options
        super().__init__(
            parent, text=name, command=self.toggle_menu, corner_radius=0, fg_color=parent.cget('bg_color')
        )
        self.dropdown = CTkFrame(root)
        self.update()

    def add_option(self, name: str, func: Callable[[], None]) -> None:
        self.options.append((name, func))
        self.update()

    def update(self):
        for name, func in self.options:
            CTkButton(self.dropdown, text=name,
                      command=func,
                      fg_color=self.dropdown.cget("fg_color")).pack()

    def toggle_menu(self):
        if self.dropdown.winfo_ismapped():
            self.dropdown.place_forget()
        else:
            x = self.winfo_vrootx()
            y = self.winfo_vrooty() + self.winfo_height()
            self.dropdown.place(x=x, y=y, anchor='nw')
            self.dropdown.lift()

    def collapse(self):
        if self.dropdown.winfo_ismapped():
            self.dropdown.place_forget()


class TopBarButton(CTkButton):
    def __init__(self, parent, name: str, command: Callable[[], None]) -> None:
        super().__init__(
            parent, text=name, command=command, corner_radius=0, fg_color=parent.cget('bg_color')
        )

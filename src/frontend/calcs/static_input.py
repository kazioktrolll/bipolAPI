"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkLabel
from ..advanced_entry import EntryWithInstructionsBlock, EntryWithInstructions
from ..help_top_level import HelpTopLevel
from ...backend import handle_crash


class StaticInputPanel(CTkFrame):
    def __init__(self, parent, center_of_mass: tuple[float, float, float]):
        super().__init__(parent)
        self.center_of_mass = center_of_mass
        self.mass_label = CTkLabel(self, width=120, anchor='e')
        self.mass_entry = EntryWithInstructionsBlock(self, on_enter=self.set_mass, instructions=('x', 'y', 'z'),
                                                     width=38, padx=1, fg_color='transparent')
        self.height = 0
        self.height_label = CTkLabel(self, width=120, anchor='e')
        self.height_entry = EntryWithInstructions(self, self.set_height, 'altitude', width=120)

        for i, val in enumerate(self.center_of_mass):
            self.set_mass(i, str(val))
        self.set_height('0')
        self.build()

    def build(self):
        CTkLabel(self, text='Center of Mass', width=120, anchor='e').grid(column=0, row=0, padx=3)
        self.columnconfigure(1, weight=1)
        self.mass_label.grid(column=2, row=0, padx=3, pady=3)
        self.mass_entry.grid(column=3, row=0, padx=3, pady=3)

        CTkLabel(self, text='Altitude', width=120, anchor='e').grid(column=0, row=1, padx=3, pady=3)
        self.height_label.grid(column=2, row=1, padx=3, pady=3)
        self.height_entry.grid(column=3, row=1, padx=3, pady=3)

    @handle_crash
    def set_mass(self, i: int, val: str):
        vals = list(self.center_of_mass)
        try:
            vals[i] = float(val)
        except ValueError:
            HelpTopLevel(None, 'Values must be numeric.')
            return
        x, y, z = vals
        self.center_of_mass = (x, y, z)
        self.mass_label.configure(text=f'({round(x, 3)} , {round(y, 3)} , {round(z, 3)})')

    @handle_crash
    def set_height(self, raw: str):
        try:
            value = int(raw)
        except ValueError:
            self.height_entry.flash()
            HelpTopLevel(None, 'Values must be numeric.')
            return
        if not 0 <= value <= 8e4:
            self.height_entry.flash()
            HelpTopLevel(None, 'Altitude must be between 0 and 80,000 m.')
            return
        self.height_entry.clear()
        self.focus_set()
        self.height = value
        self.height_label.configure(text=str(value))

    def get_data(self, size: int):
        return {
            'X_cg': [self.center_of_mass[0]] * size,
            'Y_cg': [self.center_of_mass[1]] * size,
            'Z_cg': [self.center_of_mass[2]] * size,
        }

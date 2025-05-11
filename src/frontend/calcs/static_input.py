"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkButton, CTkLabel
from ..entry_with_instructions import EntryWithInstructionsBlock
from ..help_top_level import HelpTopLevel


class StaticInputPanel(CTkFrame):
    def __init__(self, parent, center_of_mass: tuple[float, float, float]):
        super().__init__(parent)
        self.center_of_mass = center_of_mass
        self.mass_label = CTkLabel(self, width=120, anchor='e')
        self.mass_entry = EntryWithInstructionsBlock(self, ('x', 'y', 'z'), 40, 1, fg_color='transparent')
        self.set_button = CTkButton(self, text='Set', width=40, command=self.set_mass)

        self.set_mass(center_of_mass)
        self.build()

    def build(self):
        CTkLabel(self, text='Center of Mass', width=120, anchor='e').grid(column=0, row=0, padx=3)
        self.columnconfigure(1, weight=1)
        self.mass_label.grid(column=2, row=0, padx=3)
        self.mass_entry.grid(column=3, row=0, padx=3)
        self.set_button.grid(column=4, row=0, padx=3)

    def set_mass(self, values: tuple[float, float, float] = None):
        if not values:
            try:
                raws = self.mass_entry.get()
                for i, raw in enumerate(raws):
                    if raw == '': raws[i] = self.center_of_mass[i]
                x, y, z = map(float, raws)
                self.set_mass((x, y, z))
            except ValueError:
                HelpTopLevel(None, 'Values must be numeric.')
            return
        x, y, z = values
        self.mass_entry.clear()
        self.focus_set()
        self.center_of_mass = (x, y, z)
        self.mass_label.configure(text=f'({round(x, 3)} , {round(y, 3)} , {round(z, 3)})')

    def get_data(self, size: int):
        return {
            'X_cm': [self.center_of_mass[0]] * size,
            'Y_cm': [self.center_of_mass[1]] * size,
            'Z_cm': [self.center_of_mass[2]] * size,
        }

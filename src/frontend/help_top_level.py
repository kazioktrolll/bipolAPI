"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkLabel
from typing import Literal
from .popup import Popup
import textwrap


class HelpTopLevel(Popup):
    def __init__(self, master, message, padding=15, max_width=30, position: Literal['center', 'cursor'] = 'center'):
        super().__init__(master, position)

        # Wrap text into lines to make it roughly square
        for i, paragraph in enumerate(message.splitlines()):
            wrapped_text = textwrap.fill(paragraph, width=max_width)

            # Create label to display text
            label = CTkLabel(self.frame, text=wrapped_text, padx=padding, pady=padding, anchor="w", fg_color='transparent')
            label.grid(column=0, row=i)

        self.run()

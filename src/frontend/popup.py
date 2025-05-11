"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkToplevel, CTkFrame, CTkButton
from typing import Literal


class Popup(CTkToplevel):
    def __init__(self, master: CTkFrame | None, position: Literal['center', 'cursor'] = 'center'):
        super().__init__(master)
        self.position = position
        self.overrideredirect(True)
        self.bind("<Escape>", lambda _: self.destroy())
        self.frame = CTkFrame(self, width=0, height=0, fg_color='transparent')
        self.frame.grid(row=1, column=1, sticky="nsew")
        CTkButton(
            self, text='x', command=self.destroy, fg_color='red3', hover_color='red4', width=1, height=1
        ).grid(row=0, column=2)
        self.columnconfigure(0, weight=0, minsize=20)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0, minsize=20)
        self.rowconfigure(0, weight=0, minsize=20)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0, minsize=20)

    def run(self):
        self.wm_geometry("")
        self.resizable(False, False)  # Disable resizing
        self.transient()
        self.grab_set()
        self.focus_force()

        def position():
            w = self.winfo_width()
            h = self.winfo_height()
            match self.position:
                case 'cursor':
                    x = self.winfo_pointerx()
                    y = self.winfo_pointery()
                case 'center':
                    x = (self.winfo_screenwidth() - w) // 2
                    y = (self.winfo_screenheight() - h) // 2
                case _:
                    raise NotImplementedError
            self.geometry(f"{w}x{h}+{x}+{y}")

        self.after(80, position)  # noqa

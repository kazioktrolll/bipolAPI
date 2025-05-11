"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkLabel, CTkButton
from .popup import Popup


class AskPopup:
    @classmethod
    def ask(cls, question: str, options: list[str], default: str):
        assert len(options) >= 2
        popup = Popup(None)
        CTkLabel(popup.frame, text=question).grid(column=0, row=0, columnspan=len(options), sticky='nsew')

        clicked: str = default

        def on_click(_i):
            nonlocal clicked
            clicked = options[_i]
            popup.destroy()

        for i in range(len(options)):
            CTkButton(popup.frame, text=options[i], command=lambda _i=i: on_click(_i), width=60
                      ).grid(column=i, row=1)

        popup.run()
        popup.wait_window()
        return clicked

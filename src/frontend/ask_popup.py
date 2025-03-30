from customtkinter import CTkLabel, CTkButton
from .popup import Popup


class AskPopup:
    @classmethod
    def ask(cls, question: str, options: list[str], default: str):
        assert len(options) >= 2
        popup = Popup(None)
        CTkLabel(popup, text=question).grid(column=0, row=0, columnspan=len(options), sticky='nsew')

        clicked: str = default
        def on_click(_i):
            nonlocal clicked
            clicked = options[_i]
            popup.destroy()

        for i in range(len(options)):
            CTkButton(popup, text=options[i], command=lambda _i=i: on_click(_i), width=60
                      ).grid(column=i, row=1)

        popup.run()
        popup.wait_window()
        return clicked

from customtkinter import CTkLabel
from .popup import Popup
import textwrap


class HelpTopLevel(Popup):
    def __init__(self, master, message, padding=10, max_width=30):
        super().__init__(master)

        # Wrap text into lines to make it roughly square
        for i, paragraph in enumerate(message.splitlines()):
            wrapped_text = textwrap.fill(paragraph, width=max_width)

            # Create label to display text
            label = CTkLabel(self, text=wrapped_text, padx=padding, pady=padding, anchor="w")
            label.grid(column=0, row=i)

        self.run()
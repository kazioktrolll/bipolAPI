"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCheckBox
from .help_top_level import HelpTopLevel
from typing import Callable


class ParameterField(CTkFrame):
    """
    A widget for displaying and easily changing a parameter.

    Consists of a label with parameter's name, a label with parameter's current value, an entry for inputting a new value,
    and a button to confirm the change.

    After pressing the 'Set' button, the value from the entry is set as the new value, the entry clears and loses focus.
    Optionally, a given function is called with the new value as an argument.

    Attributes:
        name (str): Name of the parameter.
        value (float): Current value of the parameter.
        on_set (Optional[Callable[[float], None]]): Function to be called when the parameter is changed.
    """

    def __init__(self, master: CTkFrame,
                 name: str,
                 help_message: str,
                 on_set: Callable[[float], None] = lambda _: None,
                 assert_test: Callable[[float], bool] = lambda _: True,
                 mode: str = 'val'
                 ) -> None:
        """
        Parameters:
            master (CTkFrame): Parent widget.
            name (str): Name of the parameter.
            help_message (str): Contents of the 'Help' window shown by pressing the '?' button.
            on_set (Callable[[float], None], optional): Function to be called when the parameter is changed.
            assert_test (Callable[[float], bool], optional): A condition the new parameter has to fulfill when changed.
        """

        super().__init__(master, fg_color=master.cget('fg_color'))

        self.name = name
        self.help_message = help_message
        self.mode = mode
        self.on_set = on_set
        self.assert_test = assert_test
        self.value = 0
        self.has_message = help_message != ""

        # Set the display
        self.help_button = CTkButton(self, text='?', width=10, height=10, command=lambda: HelpTopLevel(self, self.help_message))
        self.name_label = CTkLabel(self, text=name)
        self.value_label = CTkLabel(self, text=str(self.value))
        match self.mode:
            case 'val':
                self.entry = CTkEntry(self)
                self.set_button = CTkButton(self, text="Set", width=30, command=self.set)
            case 'bool':
                self.entry = CTkCheckBox(self, text='', width=170, command=self.set)
                self.entry.select()
            case _:
                raise ValueError

        self.build()

    def build(self):
        if self.has_message: self.help_button.grid(column=0, row=0, sticky="w")
        self.name_label.grid(column=1, row=0, sticky="w")
        self.value_label.grid(column=2, row=0, sticky="w", padx=10)
        self.entry.grid(column=3, row=0, sticky="ew")
        if self.mode == 'val': self.set_button.grid(column=4, row=0, sticky="e")

    def set_entry(self, value: float | str) -> bool:
        assert isinstance(self.entry, CTkEntry)
        if value is None: value = self.entry.get()
        if value == '': return False  # When the entry is empty

        try:
            self.value = float(value)
        except ValueError:
            ParameterField.raise_bad_input('Value must be numeric.')
            return False

        if not self.assert_test(self.value):
            ParameterField.raise_bad_input('Value does not meet requirements.\nCheck the help button [?] for more info.')
            return False

        self.entry.delete(0, "end")
        self.value_label.configure(text=str(round(self.value, 2)))
        self.focus()
        self.on_set(self.value)
        return True

    def set_checkbox(self) -> bool:
        assert isinstance(self.entry, CTkCheckBox)
        self.value = self.entry.get()
        self.on_set(self.value)
        return True

    def set(self, value: float = None) -> bool:
        """Sets the value in the entry as the new value of the parameter. Returns True if changed successfully."""
        if isinstance(self.entry, CTkCheckBox):
            return self.set_checkbox()
        elif isinstance(self.entry, CTkEntry):
            return self.set_entry(value)
        raise NotImplementedError

    @classmethod
    def raise_bad_input(cls, message: str) -> None:
        HelpTopLevel(None, message)

    def disable(self) -> None:
        """Disables the change of the parameter."""
        self.set_button.configure(state="disabled", fg_color="gray40", text_color="white")
        self.entry.configure(state="disabled")

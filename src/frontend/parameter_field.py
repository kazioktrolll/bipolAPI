"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkCheckBox
from .advanced_entry import AdvancedEntry
from .help_top_level import HelpTopLevel
from .advanced_entry import EntryWithInstructionsBlock
from ..backend import handle_crash
from typing import Callable, Literal, Union


value_types = Union[bool, float, tuple[float, ...]]


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
                 on_set: Callable[[value_types], None] = lambda _: None,
                 assert_test: Callable[[value_types], bool] = lambda _: True,
                 mode: Literal['bool', 'float', 'Vector2', 'Vector3'] = 'float',
                 unit: str = 'm'
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
        self.value: value_types
        self.has_message = help_message != ""

        # Set the display
        self.help_button = CTkButton(self, text='?', width=10, height=10, command=lambda: HelpTopLevel(self, self.help_message))
        self.name_label = CTkLabel(self, text=name)
        match self.mode:
            case 'bool':
                self.entry = CTkCheckBox(self, text='', width=120, command=self.set_checkbox)
                self.value = False
                self.entry.select()
            case 'float':
                self.entry = AdvancedEntry(self, on_enter=self.set_entry, width=120)
                self.value = 0.0
            case 'Vector2':
                self.entry = EntryWithInstructionsBlock(self, self.set_entry_block, ('', ''),
                                                        width=120, padx=2, fg_color='transparent')
                self.value = (0.0, 0.0)
            case 'Vector3':
                self.entry = EntryWithInstructionsBlock(self, self.set_entry_block, ('', '', ''),
                                                        width=120, padx=2, fg_color='transparent')
                self.value = (0.0, 0.0, 0.0)
            case _:
                raise ValueError

        self.value_label = CTkLabel(self, text=str(self.value))
        self.unit_label = CTkLabel(self, text=unit)
        self.build()

    def build(self):
        self.columnconfigure(0, minsize=10)
        if self.has_message: self.help_button.grid(column=0, row=0, sticky="w")
        self.name_label.grid(column=1, row=0, sticky="w", padx=5)
        self.columnconfigure(2, weight=1)
        self.value_label.grid(column=3, row=0, sticky="w", padx=10)
        self.columnconfigure(4, minsize=120)
        self.entry.grid(column=4, row=0, sticky="ew")
        self.unit_label.grid(column=5, row=0, sticky="w", padx=5)
        self.columnconfigure(5, minsize=40)

    @handle_crash
    def set_entry(self, value: float | str) -> bool:
        """Sets the value of the parameter, if the input device is an Entry."""
        assert isinstance(self.entry, AdvancedEntry)
        if value is None: value = self.entry.get()
        if value == '': return False  # When the entry is empty

        try:
            self.value = float(value)
        except ValueError:
            self.raise_bad_input('Value must be numeric.')
            return False

        if not self.assert_test(self.value):
            self.raise_bad_input('Value does not meet requirements.\nCheck the help button [?] for more info.')
            return False

        self.entry.delete(0, "end")
        self.value_label.configure(text=str(round(self.value, 3)))
        self.focus()
        self.on_set(self.value)
        return True

    @handle_crash
    def set_entry_block(self, i: int, val: str) -> bool:
        """Sets the value of the parameter, if the input device is an EntryBlock."""
        assert isinstance(self.entry, EntryWithInstructionsBlock)
        values = list(map(str, self.value))
        values[i] = val

        try:
            self.value = tuple(map(float, values))
        except ValueError:
            self.raise_bad_input('Values must be numeric.')
            return False

        if not self.assert_test(self.value):
            self.raise_bad_input('Value does not meet requirements.\nCheck the help button [?] for more info.')
            return False

        self.entry.clear()
        val_str = ', '.join(map(lambda v: str(round(v, 3)), self.value))
        self.value_label.configure(text=val_str)
        self.focus()
        self.on_set(self.value)
        return True

    @handle_crash
    def set_checkbox(self) -> bool:
        """Sets the value of the parameter, if the input device is a Checkbox."""
        assert isinstance(self.entry, CTkCheckBox)
        self.value = self.entry.get()
        self.on_set(self.value)
        return True

    def raise_bad_input(self, message: str) -> None:
        if isinstance(self.entry, (AdvancedEntry, EntryWithInstructionsBlock)):
            self.entry.flash()
        HelpTopLevel(None, message)

    def disable(self) -> None:
        """Disables the change of the parameter."""
        self.entry.configure(state="disabled")

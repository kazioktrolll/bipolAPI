from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton
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
        self.on_set = on_set
        self.assert_test = assert_test
        self.value = 0

        # Set the display
        if not help_message == "":
            self.help_button = CTkButton(self, text='?', width=10, height=10, command=lambda: HelpTopLevel(self, self.help_message))
            self.help_button.grid(column=0, row=0, sticky="w")

        self.name_label = CTkLabel(self, text=name)
        self.name_label.grid(column=1, row=0, sticky="w")

        self.value_label = CTkLabel(self, text=str(self.value))
        self.value_label.grid(column=2, row=0, sticky="w", padx=10)

        self.entry = CTkEntry(self)
        self.entry.grid(column=3, row=0, sticky="ew")

        self.set_button = CTkButton(self, text="Set", width=30, command=self.set)
        self.set_button.grid(column=4, row=0, sticky="e")

    def set(self, value: float = None) -> bool:
        """Sets the value in the entry as the new value of the parameter. Returns True if changed successfully."""
        if value is None: value = self.entry.get()
        if value == '': return False  # When the entry is empty
        self.value = float(value)
        if not self.assert_test(self.value): return False # When the new value doesn't fulfill the design criteria
        self.entry.delete(0, "end")
        self.value_label.configure(text=value)
        self.focus()
        self.on_set(self.value)
        return True

    def disable(self) -> None:
        """Disables the change of the parameter."""
        self.set_button.configure(state="disabled", fg_color="gray40", text_color="white")
        self.entry.configure(state="disabled")

    def grid_def(self, row: int, column: int) -> None:
        self.grid(row=row, column=column, sticky="nsew", padx=10, pady=5)

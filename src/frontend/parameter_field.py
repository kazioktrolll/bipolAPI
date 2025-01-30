from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton
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
    def __init__(self, master:CTkFrame,
                 name: str,
                 on_set: Callable[[float], None]=lambda: None
                 ) -> None:
        """
        Parameters:
            master (CTkFrame): Parent widget.
            name (str): Name of the parameter.
            on_set (Optional[Callable[[float], None]]): Function to be called when the parameter is changed.
        """

        super().__init__(master)
        self.name = name
        self.on_set = on_set
        self.value = 0

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

        # Set the display
        CTkLabel(self, text=name).grid(column=0, row=0, sticky="w")
        self.value_label = CTkLabel(self, text=str(self.value))
        self.value_label.grid(column=1, row=0, sticky="w", padx=10)
        self.entry = CTkEntry(self)
        self.entry.grid(column=2, row=0, sticky="ew")
        CTkButton(self, text="Set", width=30, command=self.set).grid(column=3, row=0, sticky="e")

    def set(self) -> None:
        """Sets the value in the entry as the new value of the parameter."""
        value = self.entry.get()
        if not value: return    # When the entry is empty
        self.value = float(value)
        self.entry.delete(0, "end")
        self.value_label.configure(text=value)
        self.on_set(self.value)

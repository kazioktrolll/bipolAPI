from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkToplevel
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
                 on_set: Callable[[float], None] = lambda _: None
                 ) -> None:
        """
        Parameters:
            master (CTkFrame): Parent widget.
            name (str): Name of the parameter.
            help_message (str): Contents of the 'Help' window shown by pressing the '?' button.
            on_set (Callable[[float], None], optional): Function to be called when the parameter is changed.
        """

        super().__init__(master)
        self.configure(fg_color=master.cget('fg_color'))

        self.name = name
        self.help_message = help_message
        self.on_set = on_set
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

    def set(self, value: float = None) -> None:
        """Sets the value in the entry as the new value of the parameter."""
        if value is None: value = self.entry.get()
        if value == '': return  # When the entry is empty
        self.value = float(value)
        self.entry.delete(0, "end")
        self.value_label.configure(text=value)
        self.focus()
        self.on_set(self.value)

    def disable(self) -> None:
        """Disables the change of the parameter."""
        self.set_button.configure(state="disabled", fg_color="gray40", text_color="white")
        self.entry.configure(state="disabled")

    def grid_def(self, row: int, column: int) -> None:
        self.grid(row=row, column=column, sticky="nsew", padx=10, pady=5)


import textwrap


class HelpTopLevel:
    def __init__(self, master, message, padding=10, max_width=30):
        self.top = CTkToplevel(master)
        self.top.title("Message")

        # Wrap text into lines to make it roughly square
        wrapped_text = textwrap.fill(message, width=max_width)

        # Create label to display text
        label = CTkLabel(self.top, text=wrapped_text, padx=padding, pady=padding)
        label.pack()

        # Calculate required window size
        self.top.update_idletasks()  # Ensure size calculations are correct
        width = label.winfo_reqwidth() + padding
        height = label.winfo_reqheight() + padding

        self.top.geometry(f"{width}x{height}")  # Set window size
        self.top.resizable(False, False)  # Disable resizing
        self.top.transient(master)
        self.top.grab_set()

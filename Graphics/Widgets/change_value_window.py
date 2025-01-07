from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton


class ChangeValueWindow(CTkFrame):
    def __init__(self, master, value_name:str, initial_value=0.0, **kwargs):
        super().__init__(master, **kwargs)
        self.value_name = value_name
        self.value = initial_value

        CTkLabel(self, text=value_name).grid(row=0, column=0, padx=10, pady=10)
        self.current_value_label = CTkLabel(self, text=f"{initial_value}")
        self.current_value_label.grid(row=0, column=1, padx=10, pady=10)
        self.new_value_input = CTkEntry(self, width=10)
        self.new_value_input.grid(row=0, column=2, padx=10, pady=10)
        self.confirm_button = CTkButton(self, text="set", command=self.set_new_value, width=0)
        self.confirm_button.grid(row=0, column=3, padx=10, pady=10)

    def set_new_value(self):
        value = self.new_value_input.get()
        self.new_value_input.delete(0, "end")
        self.master.focus()
        if value == "":
            return
        if not value.isnumeric():
            raise ValueError("Value must be numeric")
        self.value = float(value)
        self.current_value_label.configure(text=value)
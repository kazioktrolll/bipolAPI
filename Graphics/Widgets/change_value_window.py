from collections.abc import Callable

from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton


class ChangeValueWindow(CTkFrame):
    def __init__(self, master, value_name:str, initial_value=0.0, do_on_set:Callable[[str, float], None]=None, **kwargs):
        super().__init__(master, **kwargs)
        self.value_name = value_name
        self.value = initial_value
        self.do_on_set = do_on_set if do_on_set else lambda name, value: None

        self.configure(corner_radius=0)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)

        CTkLabel(self, text=value_name).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.current_value_label = CTkLabel(self, text=f"{initial_value}")
        self.current_value_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.new_value_input = CTkEntry(self, width=60)
        self.new_value_input.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.confirm_button = CTkButton(self, text="set", command=self.set_new_value, width=0)
        self.confirm_button.grid(row=0, column=3, padx=10, pady=10, sticky="e")

    def set_new_value(self):
        value = self.new_value_input.get()
        self.new_value_input.delete(0, "end")
        self.master.focus()
        if value == "":
            return
        if ',' in value:
            value = value.replace(',', '.')
        try:
            float(value)
        except ValueError:
            raise ValueError("Invalid value")
        self.value = float(value)
        self.current_value_label.configure(text=str(float(value)))
        self.do_on_set(self.value_name, self.value)


class ChangeValuesMenu(CTkFrame):
    def __init__(self, master, names: list[str], initial_values: dict[str, float]=None, do_on_set_functions: list[Callable[[str, float], None]]=None, **kwargs):
        super().__init__(master, **kwargs)
        n_of_elements = len(names)
        if initial_values is None:
            initial_values = [0.0] * n_of_elements
        if do_on_set_functions is None:
            do_on_set_functions = [lambda n, v: None] * n_of_elements
        if len(initial_values) != n_of_elements or len(do_on_set_functions) != n_of_elements:
            raise ValueError("Each must be of the same length")

        self.windows = []
        for i, name, value, do_on_set in zip(range(n_of_elements), names, initial_values, do_on_set_functions):
            self.rowconfigure(i, weight=0)
            window = ChangeValueWindow(self, name, value, do_on_set)
            window.grid(row=i, column=0, sticky="ew")

    def grid(self, **kwargs):
        super().grid(**kwargs)
        max_width_names = 0
        max_width_values = 0
        for window in self.windows:
            nw = window.children[1].winfo_width()
            vw = window.children[2].winfo_width()
            if nw > max_width_names:
                max_width_names = nw
            if vw > max_width_values:
                max_width_values = vw

        for window in self.windows:
            window.children[1].configure(width=max_width_names)
            window.children[2].configure(width=max_width_values)

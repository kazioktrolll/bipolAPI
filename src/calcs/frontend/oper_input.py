from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkOptionMenu, CTk, DoubleVar
from typing import Literal


Gridable = CTk | CTkFrame


class OperInput(CTkFrame):
    def __init__(self, master: Gridable, name: str, key: str, master_grid: Gridable = None, master_row=0, control_surfaces: list[str] = None):
        super().__init__(master)
        self.value = DoubleVar(value=0.0)
        self.key = key
        self.master_grid = master_grid or self
        self.master_row = master_row
        self.bind_options = {
                    'Alpha': 'a',
                    'Beta': 'b',
                    'Roll Rate': 'r',
                    'Pitch Rate': 'p',
                    'Yaw Rate': 'y',
                    'CL': 'c',
                    'CY': 's',
                    'Roll Moment': 'rm',
                    'Pitching Moment': 'pm',
                    'Yaw Moment': 'ym'
                }
        if name in self.bind_options: del self.bind_options[name]
        if control_surfaces: self.bind_options |= {cs: f'd{i}' for i, cs in enumerate(control_surfaces)}
        self.name_label = CTkLabel(self.master_grid, text=name)
        self.bind_menu = CTkOptionMenu(self.master_grid, width=80, values=[name for name, _ in self.bind_options.items()])
        self.value_label = CTkLabel(self.master_grid, textvariable=self.value)
        self.entry = CTkEntry(self.master_grid)
        self.set_button = CTkButton(self.master_grid, text="Set", width=30, command=self.set_value)
        self.bind_button = CTkButton(self.master_grid, text="Bind", width=20, command=self.bind_switch)
        self.bound = False
        self.initialized = False

        self.build()

    def set_value(self, value:float=None):
        if value is None:
            try:
                self.set_value(float(self.entry.get()))
                self.entry.delete(0, 'end')
                self.focus_set()
                return
            except ValueError: return
        self.value.set(value)

    def bind_switch(self):
        self.bound = not self.bound
        self.build()

    def build(self):
        r = self.master_row
        if not self.bound: self.bind_menu.grid_forget()
        else: self.bind_menu.grid(row=r, column=1)

        if self.initialized: return
        self.name_label.grid(row=r, column=0)
        self.value_label.grid(row=r, column=2, padx=5)
        self.entry.grid(row=r, column=3)
        self.set_button.grid(row=r, column=4)
        self.bind_button.grid(row=r, column=5)
        self.initialized = True

    def grid(self, **kwargs):
        if self.master_grid is not self: raise PermissionError('Cannot grid a OperInput if master_grid was given!')
        super().grid(**kwargs)

    @classmethod
    def by_template(cls, master:CTk|CTkFrame, template: Literal['a', 'b', 'r', 'p', 'y'],
                    master_grid: Gridable = None, master_row=0,
                    control_surfaces: list[str] = None) -> 'OperInput':
        name = {'a':'Alpha', 'b':'Beta', 'r':'Roll Rate', 'p':'Pitch Rate', 'y':'Yaw Rate'}[template]
        return cls(master=master, name=name, key=template, master_grid=master_grid, master_row=master_row, control_surfaces=control_surfaces)

    def command_string(self) -> str:
        if not self.bound: return f"{self.key} {self.key} {self.value.get()}"
        bound_key = self.bind_options[self.bind_menu.get()]
        return f"{self.key} {bound_key} {self.value.get()}"

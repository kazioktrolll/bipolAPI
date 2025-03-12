from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkOptionMenu, CTk, DoubleVar
from ..strip_manager import RowManager


Gridable = CTk | CTkFrame


class OperInput(RowManager):
    base_names = {
        'Alpha': ('A', 'alpha'),
        'Beta': ('B', 'beta'),
        'Roll Rate': ('R', 'pb/2V'),
        'Pitch Rate': ('P', 'qc/2V'),
        'Yaw Rate': ('Y', 'rb/2V')
    }
    bindable_names = {
        'CL': ('c', 'CL'),
        'CY': ('s', 'CY'),
        'Roll Moment': ('rm', 'Cl roll mom'),
        'Pitch Moment': ('pm', 'Cm pitchmom'),
        'Yaw Moment': ('ym', 'Cn yaw mom')
    }

    def __init__(self, grid: Gridable, name: str, master_row:int=None, control_surfaces: list[str] = None):
        super().__init__(grid, master_row)
        self.value = DoubleVar(value=0.0)

        self.base_names = OperInput.base_names | {ctrl: (f'd{i}', ctrl) for i, ctrl in enumerate(control_surfaces)}
        self.bindable_names = self.base_names | OperInput.bindable_names
        del self.bindable_names[name]

        if name not in self.base_names.keys(): raise ValueError("Invalid name")
        self.display_name = name
        self.command_name = self.base_names[name][0]
        self.run_file_name = self.base_names[name][1]

        self.name_label = CTkLabel(self.grid, text=self.display_name, anchor='e')
        self.bind_menu = CTkOptionMenu(self.grid, width=120, values=list(self.bindable_names.keys()))
        self.series_manager = SeriesConfig(self.grid)
        self.value_label = CTkLabel(self.grid, textvariable=self.value)
        self.entry = CTkEntry(self.grid)
        self.set_button = CTkButton(self.grid, text="Set", width=30, command=self.set_value)
        self.bind_button = CTkButton(self.grid, text="Bind", width=20, command=self.bind_switch)

        self.bound = False
        self.build()

    def set_value(self, value:float=None):
        if value is None:
            try:
                self.set_value(float(self.entry.get()))
                self.entry.delete(0, 'end')
                self.grid.focus_set()
                return
            except ValueError: return
        self.value.set(value)

    def bind_switch(self):
        self.bound = not self.bound
        self.update()

    def update(self):
        if not self.bound: self.bind_menu.grid_forget()
        else: self.bind_menu.grid(column=1, row=self.master_index)

    def build(self):
        self.grid.columnconfigure(1, minsize=120)
        self.stack(self.name_label, sticky='e')
        self.stack([
            self.bind_menu,
            self.series_manager,
        ])
        self.stack(self.value_label, padx=5)
        self.stack([
            self.entry,
            self.set_button,
            self.bind_button
        ])
        self.update()

    def command_string(self) -> str:
        if not self.bound:
            return f"{self.command_name} {self.command_name} {self.value.get()}"
        bound_command_name = self.bindable_names[self.bind_menu.get()][0]
        return f"{self.command_name} {bound_command_name} {self.value.get()}"

    def run_file_string(self) -> str:
        if not self.bound:
            return f"{self.run_file_name} -> {self.run_file_name} = {self.value.get()}"
        bound_run_file_name = self.bindable_names[self.bind_menu.get()][1]
        return f"{self.run_file_name} -> {bound_run_file_name} = {self.value.get()}"


class OperInputPanel(CTkFrame):
    def __init__(self, parent: Gridable, control_surfaces: list[str] = None):
        super().__init__(parent)
        self.ois: list[OperInput] = [
            OperInput(grid=self, name='Alpha', master_row=0, control_surfaces=control_surfaces)
        ]
        for i, name in enumerate(self.ois[0].base_names.keys()):
            if i == 0: continue
            self.ois.append(
                OperInput(grid=self, name=name, master_row=i, control_surfaces=control_surfaces)
            )

    def run_file_string(self) -> str:
        return "\n".join([oi.run_file_string() for oi in self.ois]) + "\n"


class SeriesConfig(CTkFrame):
    def __init__(self, parent: Gridable):
        super().__init__(parent)
        CTkOptionMenu(self, values=['Constant', 'Range', 'From File']).grid(column=0, row=0)

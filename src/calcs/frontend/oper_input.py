from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkOptionMenu, CTk, DoubleVar


Gridable = CTk | CTkFrame


class OperInput(CTkFrame):
    def __init__(self, master: Gridable, name: str,
                 master_grid = False, master_row:int=None,
                 control_surfaces: list[str] = None):

        super().__init__(master)
        self.value = DoubleVar(value=0.0)

        self.master_grid = master if master_grid else self
        self.master_row = master_row if master_grid else 0


        self.base_names = {
            'Alpha': ('A', 'alpha'),
            'Beta': ('B', 'beta'),
            'Roll Rate': ('R', 'pb/2V'),
            'Pitch Rate': ('P', 'qc/2V'),
            'Yaw Rate': ('Y', 'rb/2V')
        } | {ctrl: (f'd{i}', ctrl) for i, ctrl in enumerate(control_surfaces)}
        self.bindable_names = {
            'CL': ('c', 'CL'),
            'CY': ('s', 'CY'),
            'Roll Moment': ('rm', 'Cl roll mom'),
            'Pitch Moment': ('pm', 'Cm pitchmom'),
            'Yaw Moment': ('ym', 'Cn yaw mom')}

        if name not in self.base_names.keys(): raise ValueError("Invalid name")
        self.display_name = name
        self.command_name = self.base_names[name][0]
        self.run_file_name = self.base_names[name][1]

        self.name_label = CTkLabel(self.master_grid, text=self.display_name)
        self.bind_menu = CTkOptionMenu(self.master_grid, width=80, values=list(self.bindable_names.keys()))
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
            OperInput(master=self, name='Alpha', master_grid=True, master_row=0, control_surfaces=control_surfaces)
        ]
        for i, name in enumerate(self.ois[0].base_names.keys()):
            if i == 0: continue
            self.ois.append(
                OperInput(master=self, name=name, master_grid=True, master_row=i, control_surfaces=control_surfaces)
            )

    def run_file_string(self) -> str:
        return "\n".join([oi.run_file_string() for oi in self.ois]) + "\n"

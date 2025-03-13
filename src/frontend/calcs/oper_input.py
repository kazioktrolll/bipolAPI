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
            self.bind_menu
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


class OperSeriesInput(RowManager):
    def __init__(self, grid: Gridable, name: str, master_row:int=None, control_surfaces: list[str] = None):
        super().__init__(grid, master_row)

        self.base_names = OperInput.base_names | {ctrl: (f'd{i}', ctrl) for i, ctrl in enumerate(control_surfaces)}
        self.bindable_names = self.base_names | OperInput.bindable_names
        del self.bindable_names[name]

        if name not in self.base_names.keys(): raise ValueError("Invalid name")
        self.display_name = name
        self.command_name = self.base_names[name][0]
        self.run_file_name = self.base_names[name][1]

        self.name_label = CTkLabel(self.grid, text=self.display_name, anchor='e')
        self.bind_menu = CTkOptionMenu(self.grid, width=120, values=list(self.bindable_names.keys()))
        self.series_config = SeriesConfig(self.grid)
        self.set_button = CTkButton(self.grid, text="Set", width=30, command=self.set_value)
        self.bind_button = CTkButton(self.grid, text="Bind", width=20, command=self.bind_switch)

        self.bound = False
        self.build()

    def set_value(self):
        self.series_config.set_value()

    def get_value(self): return self.series_config.get_value()

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
            self.series_config,
            self.set_button,
            self.bind_button
        ])
        self.update()


class OperSeriesInputPanel(CTkFrame):
    def __init__(self, parent: Gridable, control_surfaces: list[str] = None):
        super().__init__(parent)
        self.ois: list[OperSeriesInput] = [
            OperSeriesInput(grid=self, name='Alpha', master_row=0, control_surfaces=control_surfaces)
        ]
        for i, name in enumerate(self.ois[0].base_names.keys()):
            if i == 0: continue
            self.ois.append(
                OperSeriesInput(grid=self, name=name, master_row=i, control_surfaces=control_surfaces)
            )

    def get_values(self) -> list[list[float]]:
        vals = [item.get_value() for item in self.ois]
        lists = [val for val in vals if type(val) == list]
        if len(lists) == 0: return [[val] for val in vals]
        for lst in lists:
            if len(lst) != len(lists[0]): raise ValueError("Invalid length")
        _r = []
        for val in vals:
            if type(val) == list: _r.append(val)
            if type(val) == float: _r.append([val]*len(lists[0]))
        return _r


class SeriesConfig(CTkFrame):
    def __init__(self, parent: Gridable):
        super().__init__(parent)
        self.mode_menu = CTkOptionMenu(self, values=['Constant', 'Range', 'From File'], command=self.switch_mode)
        self.mode = 'Constant'
        self.value_label = CTkLabel(self, text='0', width=40, anchor='e')
        self.constant_entry = None
        self.range_entry = None
        self.from_file_entry = None
        self.active_entry = None
        self.build()

    def build(self):
        self.mode_menu.grid(column=0, row=0)
        self.value_label.grid(column=1, row=0)
        self.constant_entry = CTkEntry(self, width=120)
        self.range_entry = CTkFrame(self, fg_color='transparent')
        for i, t in zip([0, 1, 2], ['from', 'step', 'to']):
            EntryWithInstructions(self.range_entry, t, width=40).grid(column=i, row=0)
        self.from_file_entry = CTkLabel(self, text='PLACEHOLDER', width=120)
        self.update()

    def update(self):
        self.switch_mode()

    def switch_mode(self, _=None):
        curr_active = {'Constant': self.constant_entry, 'Range': self.range_entry, 'From File': self.from_file_entry}[self.mode_menu.get()]
        if curr_active is self.active_entry: return
        if self.active_entry is not None:
            self.active_entry.grid_forget()
        self.active_entry = curr_active
        self.active_entry.grid(column=2, row=0)

    def set_value(self):
        self.mode = self.mode_menu.get()
        match self.mode:
            case 'Constant': self.value_label.configure(text=f"{self.constant_entry.get()}")
            case 'Range': self.value_label.configure(
                text=f"{self.range_entry.children['!entrywithinstructions'].get()}:"
                     f"{self.range_entry.children['!entrywithinstructions2'].get()}:"
                     f"{self.range_entry.children['!entrywithinstructions3'].get()}")
            case 'From File': self.from_file_entry.configure(text=f"{self.from_file_entry.cget('text')}")

    def get_value(self) -> float | list[float]:
        val = self.value_label.cget('text')
        match self.mode:
            case 'Constant': return float(val)
            case 'Range':
                f, s, t = map(float, val.split(':'))
                val = []
                while f <= t:
                    val.append(f)
                    f += s
                return val
            case 'From File': return -69
            case _: return -69.69


class EntryWithInstructions(CTkEntry):
    def __init__(self, parent: Gridable, instructions: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.instructions = instructions
        self.fill()
        self.bind("<FocusOut>", self.fill)
        self.bind("<FocusIn>", self.clear)

    def clear(self, _=None):
        try:
            float(self.get())
            return
        except ValueError:
            self.delete(0, 'end')
            self.configure(text_color=CTkEntry(None).cget('text_color'))

    def fill(self, _=None):
        if self.get() != '': return
        self.insert(0, self.instructions)
        self.configure(text_color='gray40')

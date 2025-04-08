from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkOptionMenu, CTk, CTkSegmentedButton
from .series_configs import SeriesConfig
from ...strip_manager import RowManager


Gridable = CTk | CTkFrame
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


class OperSeriesInput(RowManager):
    def __init__(self, grid: Gridable, name: str, master_row:int=None, control_surfaces: list[str] = None):
        super().__init__(grid, master_row)

        self.base_names = base_names | {ctrl: (f'd{i}', ctrl) for i, ctrl in enumerate(control_surfaces)}
        self.bindable_names = self.base_names | bindable_names
        del self.bindable_names[name]

        if name not in self.base_names.keys(): raise ValueError("Invalid name")
        self.display_name = name
        self.command_name = self.base_names[name][0]
        self.run_file_name = self.base_names[name][1]

        self.name_label = CTkLabel(self.grid, text=self.display_name, anchor='e')
        self.bind_menu = CTkOptionMenu(self.grid, width=120, values=list(self.bindable_names.keys()))
        self.series_config = SeriesConfig(self.grid)
        self.bind_button = CTkButton(self.grid, text="Bind", width=20, command=self.bind_switch)

        self.bound = False
        self.build()

    def get_value(self): return self.series_config.get_value()

    def bind_switch(self):
        self.bound = not self.bound
        self.update()

    def update(self):
        self.series_config.update()
        if not self.bound: self.bind_menu.grid_forget()
        else: self.bind_menu.grid(column=1, row=self.master_index)

    def build(self):
        self.grid.columnconfigure(1, minsize=120)
        self.stack(self.name_label, sticky='e')
        self.stack([
            self.bind_menu,
            self.series_config,
            self.bind_button
        ])
        self.update()

    def run_file_names(self) -> str:
        if not self.bound:
            return f"{self.run_file_name} -> {self.run_file_name}"
        bound_run_file_name = self.bindable_names[self.bind_menu.get()][1]
        return f"{self.run_file_name} -> {bound_run_file_name}"


class OperSeriesInputPanel(CTkFrame):
    def __init__(self, parent: Gridable, control_surfaces: list[str] = None):
        super().__init__(parent)
        sb = CTkSegmentedButton(self, values=['Single', 'Series'], command=self.toggle_series)
        sb.set('Single')
        sb.grid(row=0, column=2, sticky='w')
        self.load_from_file_button = CTkButton(self, text='Add File', width=1)
        self.ois: list[OperSeriesInput] = [
            OperSeriesInput(grid=self, name='Alpha', master_row=1, control_surfaces=control_surfaces)
        ]
        for i, name in enumerate(self.ois[0].base_names.keys()):
            if i == 0: continue
            self.ois.append(
                OperSeriesInput(grid=self, name=name, master_row=i+1, control_surfaces=control_surfaces)
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

    def toggle_series(self, mode: str):
        match mode:
            case 'Single':
                target = False
                self.load_from_file_button.grid_forget()
            case 'Series':
                target = True
                self.load_from_file_button.grid(row=0, column=1, sticky='ew')
            case _: raise ValueError("Invalid mode")
        for oi in self.ois:
            oi.series_config.series_enabled = target
            oi.update()

    def get_run_file_data(self) -> dict[str, list[float]]:
        names = [oi.run_file_names() for oi in self.ois]
        values = self.get_values()
        return dict(zip(names, values))

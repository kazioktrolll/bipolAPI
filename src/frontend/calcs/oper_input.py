from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkOptionMenu, CTk, CTkSegmentedButton
from abc import ABC, abstractmethod
from ..strip_manager import RowManager
from ..entry_with_instructions import EntryWithInstructions
from ..help_top_level import HelpTopLevel


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


class ConfigItem(CTkFrame, ABC):
    def __init__(self, parent: Gridable):
        super().__init__(parent, fg_color='transparent')
        self.value_label = CTkLabel(self, text='0', width=120, anchor='e')
        self.set_button = CTkButton(self, text='Set', width=40, command=self.set_value)

    @abstractmethod
    def build(self) -> None: ...

    @abstractmethod
    def set_value(self) -> None: ...

    @abstractmethod
    def get_values(self) -> float | list[float]: ...


class ConstantConfig(ConfigItem):
    def __init__(self, parent: Gridable):
        super().__init__(parent)
        self.value = 0.0
        self.entry = CTkEntry(self, width=120)
        self.build()

    def build(self) -> None:
        self.value_label.grid(column=0, row=0)
        self.entry.grid(column=1, row=0)
        self.set_button.grid(column=2, row=0)

    def set_value(self) -> None:
        val = self.entry.get()
        self.entry.delete(0, 'end')
        try: val = float(val)
        except ValueError:
            HelpTopLevel(None, 'Value must be numeric.')
            return
        self.value = val
        self.value_label.configure(text=str(round(val, 3)))

    def get_values(self): return self.value


class RangeConfig(ConfigItem):
    def __init__(self, parent: Gridable):
        super().__init__(parent)
        self.values = []
        self.entries = [EntryWithInstructions(self, t, width=40) for t in ['from', 'step', 'to']]
        self.build()

    def build(self):
        self.value_label.grid(column=0, row=0)
        for i, e in enumerate(self.entries): e.grid(column=i+1, row=0)
        self.set_button.grid(column=4, row=0)

    def set_value(self) -> None:
        try: f, s, t = map(float, [e.get() for e in self.entries])
        except ValueError:
            HelpTopLevel(None, 'Values must be numeric.')
            return
        for e in self.entries:
            e.delete(0, 'end')
            e.fill()
        self.focus_set()
        self.value_label.configure(text=f'{round(f, 3)} : {round(s, 3)} : {round(t, 3)}')
        self.values.clear()
        while f <= t:
            self.values.append(f)
            f += s

    def get_values(self) -> float | list[float]: return self.values


class FileConfig(ConfigItem):
    def __init__(self, parent: Gridable):
        super().__init__(parent)
        self.choose_file_button = CTkButton(self, text='Choose File', width=160)
        self.values: list[float] = []
        self.build()

    def build(self):
        self.value_label.grid(column=0, row=0)
        self.choose_file_button.grid(column=1, row=0, columnspan=2, sticky='ew')

    def set_value(self) -> None: pass

    def get_values(self) -> float | list[float]: return self.values


class SeriesConfig(CTkFrame):
    def __init__(self, parent: Gridable):
        super().__init__(parent)
        self.mode_menu = CTkOptionMenu(self, values=['Constant', 'Range', 'From File'], command=self.switch_mode)
        self.constant_entry = ConstantConfig(self)
        self.range_entry = RangeConfig(self)
        self.from_file_entry = FileConfig(self)
        self.active_entry = None
        self.series_enabled = False
        self.build()

    @property
    def mode(self):
        return self.mode_menu.get()

    def build(self):
        self.update()

    def update(self):
        if self.series_enabled:
            self.mode_menu.grid(column=0, row=0)
        else:
            self.mode_menu.grid_forget()
        self.switch_mode()

    def switch_mode(self, _=None):
        curr_active = {'Constant': self.constant_entry, 'Range': self.range_entry, 'From File': self.from_file_entry}[self.mode]
        if curr_active is self.active_entry: return
        if self.active_entry is not None:
            self.active_entry.grid_forget()
        self.active_entry = curr_active
        self.active_entry.grid(column=1, row=0)

    def get_value(self) -> float | list[float]: return self.active_entry.get_values()

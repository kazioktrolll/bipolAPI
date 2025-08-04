"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkOptionMenu, CTk, CTkSegmentedButton
from tkinter.filedialog import askopenfilename
from .series_configs import SeriesConfig
from .files_manager import FilesManager
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
    def __init__(self, grid: Gridable, files_manager: FilesManager, name: str, master_row: int = None, control_surfaces: list[str] = None):
        super().__init__(grid, master_row)

        self.base_names = base_names | {ctrl: (f'd{i}', ctrl) for i, ctrl in enumerate(control_surfaces)}
        self.bindable_names = self.base_names | bindable_names
        del self.bindable_names[name]

        if name not in self.base_names.keys(): raise ValueError("Invalid name")
        self.display_name = name
        self.command_name = self.base_names[name][0]
        self.run_file_name = self.base_names[name][1]

        self.name_label = CTkLabel(self.grid, text=self.display_name.capitalize(), anchor='e')
        self.bind_menu = CTkOptionMenu(self.grid, width=120, values=list(self.bindable_names.keys()))
        self.series_config = SeriesConfig(self.grid, files_manager)
        self.bind_button = CTkButton(self.grid, text="Bind", width=20, command=self.bind_switch)

        self.bound = False
        self.build()

    def get_value(self):
        return self.series_config.get_value()

    def get_size(self):
        return self.series_config.vals_size

    def bind_switch(self):
        self.bound = not self.bound
        self.update()

    def update(self):
        self.series_config.update()
        if not self.bound:
            self.bind_menu.grid_forget()
        else:
            self.bind_menu.grid(column=2, row=self.master_index, padx=4)

    def build(self):
        self.grid.columnconfigure(1, minsize=120)
        self.stack_spacing(0)
        self.stack(self.name_label, sticky='e', pady=6, padx=6)
        self.grid.columnconfigure(2, minsize=140)
        self.stack([
            self.bind_menu,
            self.series_config,
            self.bind_button
        ], padx=4, pady=6)
        self.update()

    def run_file_names(self) -> str:
        if not self.bound:
            return f"{self.run_file_name} -> {self.run_file_name}"
        bound_run_file_name = self.bindable_names[self.bind_menu.get()][1]
        return f"{self.run_file_name} -> {bound_run_file_name}"


class OperSeriesInputPanel(CTkFrame):
    def __init__(self, parent: Gridable, control_surfaces: list[str] = None):
        super().__init__(parent, fg_color='transparent', border_width=3)
        self.files_manager = FilesManager()

        sb = CTkSegmentedButton(self, values=['Single', 'Series'], command=self.toggle_series, width=100, dynamic_resizing=False)
        sb.set('Single')
        sb.grid(row=0, column=3, sticky='w', pady=10)
        self.load_from_file_button = CTkButton(self, text='Add File', width=169, command=self.add_file)
        self.ois: list[OperSeriesInput] = [
            OperSeriesInput(grid=self, files_manager=self.files_manager, name='Alpha', master_row=1, control_surfaces=control_surfaces)
        ]
        for i, name in enumerate(self.ois[0].base_names.keys()):
            if i == 0: continue
            self.ois.append(
                OperSeriesInput(grid=self, files_manager=self.files_manager, name=name, master_row=i + 1, control_surfaces=control_surfaces)
            )
        # Add padding at ends
        self.rowconfigure(20, minsize=10)
        self.columnconfigure(20, minsize=10)

    def get_values(self, forced) -> tuple[list[list[float]], int]:
        vals = [item.get_value() for item in self.ois]
        size = self.validate_vals_length(forced)

        _r = []
        for val in vals:
            if type(val) == list: _r.append(val)
            if type(val) == float: _r.append([val] * size)
        return _r, size

    def validate_vals_length(self, forced: bool) -> int:
        """Ensures the series are of the same length or constants."""
        size = 1
        for oi in self.ois:
            oi_size = oi.get_size()
            if oi_size == 1:
                continue
            if size == 1:
                size = oi_size
                continue
            if oi_size != size: raise ValueError(f"Every series has to be of the same size or constant!\nConflicting series: {oi.display_name}")
        if size >= 1000 and not forced: raise ResourceWarning
        return size

    def toggle_series(self, mode: str):
        match mode:     # noqa
            case 'Single':
                target = False
                self.load_from_file_button.grid_forget()
                for oi in self.ois:
                    oi.series_config.set_mode('Constant')
            case 'Series':
                target = True
                self.load_from_file_button.grid(row=0, column=3, sticky='e', padx=3)
            case _:
                raise ValueError("Invalid mode")
        for oi in self.ois:
            oi.series_config.series_enabled = target
            oi.update()

    def get_run_file_data(self, forced=False) -> tuple[dict[str, list[float]], int]:
        names = [oi.run_file_names() for oi in self.ois]
        values, size = self.get_values(forced)
        return dict(zip(names, values)), size

    def add_file(self) -> None:
        path = askopenfilename(
            filetypes=[('CSV File', ['*.csv'])]
        )
        self.files_manager.load_file(path)

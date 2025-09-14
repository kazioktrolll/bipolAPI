"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from tkinter.filedialog import askopenfilename

from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkOptionMenu, CTk, CTkSegmentedButton

from .files_manager import FilesManager
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
    """Represents a single parameter in the Calc menu, handles the data input and binding."""

    def __init__(self, grid: Gridable, master_row: int, files_manager: FilesManager, name: str, control_surfaces_names: list[str] = None):
        """

        :param grid: Master widget.
        :param master_row: A row number to grid the widget to.
        :param files_manager: The FilesManager instance to use for loading files.
        :param name: Name of the parameter represented.
        :param control_surfaces_names: A list with the names of all control surfaces that can be used for binding.
        """
        super().__init__(grid, master_row)

        # Load all the required names
        if name not in base_names.keys(): raise ValueError("Invalid name")
        self.display_name = name  # The name to be displayed in the UI
        self._command_name = base_names[name][0]  # The callsign to be used in AVL commands
        self._run_file_name = base_names[name][1]  # The name used in .run files

        # Names of all the other parameters this one can be bound to
        controls_names = {ctrl: (f'd{i}', ctrl) for i, ctrl in enumerate(control_surfaces_names)} if control_surfaces_names else {}
        self.bindable_names = base_names | controls_names | bindable_names
        del self.bindable_names[name]

        self.name_label = CTkLabel(self.grid, text=self.display_name.capitalize(), anchor='e')
        self.bind_menu = CTkOptionMenu(self.grid, width=120, values=list(self.bindable_names.keys()))
        self.series_config = SeriesConfig(self.grid, files_manager)
        self.bind_button = CTkButton(self.grid, text="Bind", width=20, command=self._bind_switch)

        self.bound = False
        self._build()

    def get_value(self):
        return self.series_config.get_value()

    def get_size(self):
        """Returns the number of values in the series."""
        return self.series_config.vals_size

    def _bind_switch(self):
        self.bound = not self.bound
        self.update()

    def update(self):
        self.series_config.update()
        if not self.bound:
            self.bind_menu.grid_forget()
        else:
            self.bind_menu.grid(column=2, row=self.master_index, padx=4)

    def _build(self):
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
            return f"{self._run_file_name} -> {self._run_file_name}"
        bound_run_file_name = self.bindable_names[self.bind_menu.get()][1]
        return f"{self._run_file_name} -> {bound_run_file_name}"


class OperSeriesInputPanel(CTkFrame):
    """Represents the entire main input panel for the Calc menu."""

    def __init__(self, parent: Gridable, control_surfaces: list[str] = None):
        """

        :param parent: The parent widget.
        :param control_surfaces: A list with the names of all control surfaces that can be used for binding.
        """
        super().__init__(parent, fg_color='transparent', border_width=3)
        self._files_manager = FilesManager()

        series_toggle_button = CTkSegmentedButton(self, values=['Single', 'Series'], command=self._toggle_series, width=100, dynamic_resizing=False)
        series_toggle_button.set('Single')
        series_toggle_button.grid(row=0, column=3, sticky='w', pady=10)
        self._load_from_file_button = CTkButton(self, text='Add File', width=169, command=self._add_file)
        self._ois: list[OperSeriesInput] = [
            OperSeriesInput(grid=self, files_manager=self._files_manager, name='Alpha', master_row=1, control_surfaces_names=control_surfaces)
        ]
        for i, name in enumerate(base_names.keys()):
            if i == 0: continue
            self._ois.append(
                OperSeriesInput(grid=self, files_manager=self._files_manager, name=name, master_row=i + 1, control_surfaces_names=control_surfaces)
            )
        # Add padding at ends
        self.rowconfigure(20, minsize=10)
        self.columnconfigure(20, minsize=10)

    def get_values(self, ignore_resource_warning: bool) -> tuple[list[list[float]], int]:
        """Returns a list of all the values of all the parameters and the size of the series.
        Raises a ResourceWarning if the series are too long, unless ignore_resource_warning is True."""
        # Get values of all the parameters
        vals = [item.get_value() for item in self._ois]
        # Ensure all series are of the same length or constants
        size = self._validate_vals_length(ignore_resource_warning)
        # Map all the constants into a series
        _r = []
        for val in vals:
            if type(val) == list: _r.append(val)
            if type(val) == float: _r.append([val] * size)
        return _r, size

    def _validate_vals_length(self, ignore_resource_warning: bool) -> int:
        """Ensures the series are of the same length or constants."""
        size = 1  # Default
        for oi in self._ois:
            oi_size = oi.get_size()
            if oi_size == 1:
                continue
            if size == 1:
                size = oi_size
                continue
            if oi_size != size:
                raise ValueError(f"Every series has to be of the same size or constant!\nConflicting series: {oi.display_name}")
        if size >= 1000 and not ignore_resource_warning: raise ResourceWarning
        return size

    def _toggle_series(self, mode: str):
        match mode:  # noqa
            case 'Single':
                target = False
                self._load_from_file_button.grid_forget()
                for oi in self._ois:
                    oi.series_config.set_mode('Constant')
            case 'Series':
                target = True
                self._load_from_file_button.grid(row=0, column=3, sticky='e', padx=3)
            case _:
                raise ValueError("Invalid mode")
        for oi in self._ois:
            oi.series_config._series_enabled = target  # noqa
            oi.update()

    def get_run_file_data(self, ignore_resource_warning=False) -> tuple[dict[str, list[float]], int]:
        """Returns a dict with the names of the parameters and the values of the series, as well as the size of the series."""
        names = [oi.run_file_names() for oi in self._ois]
        values, size = self.get_values(ignore_resource_warning)
        return dict(zip(names, values)), size

    def _add_file(self) -> None:
        path = askopenfilename(
            filetypes=[('CSV File', ['*.csv'])]
        )
        self._files_manager.load_file(path)

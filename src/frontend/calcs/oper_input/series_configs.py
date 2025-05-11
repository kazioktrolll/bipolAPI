"""
Code related to the direct means of input of Calc workflow.
"""

from abc import ABC, abstractmethod
from typing import final

from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkOptionMenu
from .files_manager import FilesManager
from ...popup import Popup
from ...help_top_level import HelpTopLevel
from ...entry_with_instructions import EntryWithInstructions


class ConfigItem(CTkFrame, ABC):
    def __init__(self, parent):
        super().__init__(parent, fg_color='transparent')
        self.values: list[float] | float = []
        self.value_label = CTkLabel(self, text='0', width=120, anchor='e')
        self.set_button = CTkButton(self, text='Set', width=40, command=self.set_value)
        self.nof_values_label = CTkLabel(self, text='(0)', width=30, anchor='e')

    @abstractmethod
    def build(self) -> None: ...

    @abstractmethod
    def set_value(self) -> None: ...

    @final
    def get_values(self) -> list[float]: return self.values

    @property
    @final
    def nof_values(self):
        if isinstance(self.values, int): return 1
        return len(self.values)


class ConstantConfig(ConfigItem):
    def __init__(self, parent):
        super().__init__(parent)
        self.values = 0.0
        self.nof_values_label.configure(text='')
        self.entry = CTkEntry(self, width=120)
        self.build()

    def build(self) -> None:
        self.value_label.grid(column=0, row=0, padx=3)
        self.nof_values_label.grid(column=1, row=0, padx=3)
        self.entry.grid(column=2, row=0, padx=3)
        self.set_button.grid(column=3, row=0, padx=3)

    def set_value(self) -> None:
        val = self.entry.get()
        self.entry.delete(0, 'end')
        try:
            val = float(val)
        except ValueError:
            HelpTopLevel(None, 'Value must be numeric.')
            return
        self.values = val
        self.value_label.configure(text=str(round(val, 3)))


class RangeConfig(ConfigItem):
    def __init__(self, parent):
        super().__init__(parent)
        self.values = []
        self.entries = [EntryWithInstructions(self, t, width=40) for t in ['from', 'step', 'to']]
        self.build()

    def build(self):
        self.value_label.grid(column=0, row=0, padx=3)
        self.nof_values_label.grid(column=1, row=0, padx=3)
        for i, e in enumerate(self.entries): e.grid(column=i + 2, row=0, padx=1)
        self.set_button.grid(column=5, row=0, padx=3)

    def set_value(self) -> None:
        try:
            f, s, t = map(float, [e.get() for e in self.entries])
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
        self.nof_values_label.configure(text=f'({self.nof_values})')


class FileConfig(ConfigItem):
    def __init__(self, parent, files_manager: FilesManager):
        super().__init__(parent)
        self.files_manager = files_manager
        self.choose_file_button = CTkButton(self, text='Choose File', width=160, command=self.choose_file)
        self.values: list[float] = []
        self.build()

    def build(self):
        self.value_label.grid(column=0, row=0, padx=3)
        self.nof_values_label.grid(column=1, row=0, padx=3)
        self.choose_file_button.grid(column=2, row=0, columnspan=2, sticky='ew', padx=6)

    def choose_file(self) -> None:
        popup = Popup(None)
        CTkLabel(popup.frame, text='Choose File', width=160, anchor='e').grid(column=0, row=0)
        CTkLabel(popup.frame, text='Choose Series', width=160, anchor='e').grid(column=0, row=1)
        file_menu = CTkOptionMenu(popup.frame, values=[''])
        file_menu.grid(column=1, row=0, padx=10, pady=10)
        series_menu = CTkOptionMenu(popup.frame, values=[''])
        series_menu.grid(column=1, row=1)

        def update_series(file_name):
            series_menu.configure(values=self.files_manager.series_names(file_name))

        file_menu.configure(command=update_series, values=self.files_manager.file_names)

        def set_and_close():
            file_name = file_menu.get()
            if file_name:
                series_name = series_menu.get()
                if series_name:
                    self.values = self.files_manager.files_dicts[file_name][series_name]
                    self.value_label.configure(text=f'{file_name} \\ {series_name}')
                    self.nof_values_label.configure(text=f'({self.nof_values})')
            popup.destroy()

        CTkButton(popup.frame, text='Set', command=set_and_close
                  ).grid(column=0, row=2, columnspan=2, sticky='ew', padx=10, pady=10)
        popup.run()

    def set_value(self) -> None:
        pass


class SeriesConfig(CTkFrame):
    def __init__(self, parent, files_manager: FilesManager):
        super().__init__(parent)
        self.mode_menu = CTkOptionMenu(self, values=['Constant', 'Range', 'From File'], command=self.switch_mode)
        self.constant_entry = ConstantConfig(self)
        self.range_entry = RangeConfig(self)
        self.from_file_entry = FileConfig(self, files_manager)
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
        curr_active = {
            'Constant': self.constant_entry,
            'Range': self.range_entry,
            'From File': self.from_file_entry
        }[self.mode]
        if curr_active is self.active_entry: return
        if self.active_entry is not None:
            self.active_entry.grid_forget()
        self.active_entry = curr_active
        self.active_entry.grid(column=1, row=0)

    def get_value(self) -> float | list[float]:
        return self.active_entry.get_values()

    @property
    def vals_size(self) -> int:
        vals = self.get_value()
        if isinstance(vals, float): return 1
        return len(vals)

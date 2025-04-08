from abc import ABC, abstractmethod
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkOptionMenu
from ...help_top_level import HelpTopLevel
from ...entry_with_instructions import EntryWithInstructions


class ConfigItem(CTkFrame, ABC):
    def __init__(self, parent):
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
    def __init__(self, parent):
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
    def __init__(self, parent):
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
    def __init__(self, parent):
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
    def __init__(self, parent):
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


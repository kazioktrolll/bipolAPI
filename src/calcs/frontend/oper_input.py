from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkOptionMenu, CTk, DoubleVar
from typing import Literal


Gridable = CTk | CTkFrame


class OperInput(CTkFrame):
    def __init__(self, master: Gridable,
                 key: str, name: str = None,
                 master_grid = False, master_row=None,
                 control_surfaces: list[str] = None):

        super().__init__(master)
        self.value = DoubleVar(value=0.0)

        self.master_grid = master if master_grid else self
        self.master_row = master_row if master_grid else 0

        self.bind_options = NameKeeper.full_set()
        if key in NameKeeper.builtins():
            self.name = NameKeeper(builtin=key)
        else:
            self.name = NameKeeper(name=name, dx=key)
        if control_surfaces:
            self.bind_options.extend([NameKeeper(name=surf_name, dx=f'd{i}') for i, surf_name in enumerate(control_surfaces)])
        if self.name.avl in self.bind_options.avl:
            self.bind_options.remove(self.name)

        self.name_label = CTkLabel(self.master_grid, text=self.name.display)
        self.bind_menu = CTkOptionMenu(self.master_grid, width=80, values=[display for display in self.bind_options.display])
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
    def full_set(cls, master: Gridable, master_grid = False, control_surfaces: list[str] = None) -> list['OperInput']:
        if master_grid is None:
            return [cls(master=master, key=t, control_surfaces=control_surfaces)
                    for t in ['a', 'b', 'r', 'p', 'y']]
        return [cls(master=master, key=t, master_grid=master_grid, master_row=i, control_surfaces=control_surfaces)
                for i, t in enumerate(['a', 'b', 'r', 'p', 'y'])]

    def command_string(self) -> str:
        if not self.bound:
            return f"{self.name.avl} {self.name.avl} {self.value.get()}"
        bound = self.bind_options.find_by(display=self.bind_menu.get())
        return f"{self.name.avl} {bound.avl} {self.value.get()}"

    def run_file_string(self) -> str:
        if not self.bound:
            return f"{self.name.run_file} -> {self.name.run_file} = {self.value.get()}"
        bound = self.bind_options.find_by(display=self.bind_menu.get())
        return f"{self.name.run_file} -> {bound.run_file} = {self.value.get()}"


class NameKeeper:
    def __init__(self, builtin: Literal['a', 'b', 'r', 'p', 'y']|str=None, name:str = None, dx:str = None):
        self._letter = builtin
        self._name = name
        self._dx = dx

    @property
    def avl(self) -> str:
        if self._dx: return self._dx
        return str(self._letter)

    @property
    def display(self):
        if self._name: return self._name
        return {'a':'Alpha', 'b':'Beta', 'r':'Roll Rate', 'p':'Pitch Rate', 'y':'Yaw Rate'}[self._letter]

    @property
    def run_file(self):
        if self._name: return self._name.capitalize()
        return {'a':'alpha', 'b':'beta', 'r':'pb/2V', 'p':'qc/2V', 'y':'rb/2V'}[self._letter]

    @classmethod
    def builtins(cls):
        return ['a', 'b', 'r', 'p', 'y']

    @classmethod
    def full_set(cls):
        return NameKeeperList([cls(builtin=l) for l in cls.builtins()])


class NameKeeperList:
    def __init__(self, items: list[NameKeeper]):
        self._items = items

    def __getitem__(self, item):
        return self._items[item]

    def pop(self, index):
        return self._items.pop(index)

    def remove(self, item: NameKeeper):
        self.pop(self.find(item=item))

    def extend(self, new_items: list[NameKeeper]):
        self._items.extend(new_items)

    @property
    def avl(self):
        return [item.avl for item in self._items]

    @property
    def run_file(self):
        return [item.run_file for item in self._items]

    @property
    def display(self):
        return [item.display for item in self._items]

    def find(self, item: NameKeeper):
        if item:
            for i, my_item in enumerate(self._items):
                if item.avl == my_item.avl:
                    return i

    def find_by(self, avl:str = None, display: str =None, run_name:str=None):
        if avl:
            for item in self._items:
                if avl == item.avl:
                    return item

        if display:
            for item in self._items:
                if display == item.display:
                    return item

        if run_name:
            for item in self._items:
                if run_name == item.run_file:
                    return item

        raise ValueError("No parameter given!")

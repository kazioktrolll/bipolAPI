from customtkinter import CTkFrame, CTk, CTkBaseClass
from abc import ABC, abstractmethod
from typing import final


Gridable = CTkFrame | CTk


class StripManager(ABC):
    def __init__(self, grid: Gridable, master_index: int):
        super().__init__()
        self.grid = grid
        self.curr_index = 0
        self.master_index = master_index

    @final
    def clear(self):
        children = self.grid.winfo_children()
        for child in children:
            child.grid_forget()
        self.curr_index = 0
        return children

    @abstractmethod
    def _stack(self, item: CTkBaseClass, **kwargs): ...

    @final
    def stack(self, item: CTkBaseClass | list[CTkBaseClass], **kwargs):
        if isinstance(item, CTkBaseClass):
            self._stack(item, **kwargs)
            return
        if isinstance(item, list):
            for item in item:
                self._stack(item, **kwargs)


class ColumnManager(StripManager):
    def _stack(self, item: CTkBaseClass, **kwargs):
        super().stack(item, **kwargs)
        item.grid(column=self.master_index, row=self.curr_index, **kwargs)
        self.curr_index += 1


class RowManager(StripManager):
    def _stack(self, item: CTkBaseClass, **kwargs):
        item.grid(column=self.curr_index, row=self.master_index, **kwargs)
        self.curr_index += 1

from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton
from typing import Callable, Any


class ParameterField(CTkFrame):
    def __init__(self, master:CTkFrame,
                 name: str,
                 on_set: Callable[[float], None]=lambda: None
                 ) -> None:

        super().__init__(master)
        self.name = name
        self.on_set = on_set
        self.value = 0

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

        CTkLabel(self, text=name).grid(column=0, row=0, sticky="w")
        self.value_label = CTkLabel(self, text=str(self.value))
        self.value_label.grid(column=1, row=0, sticky="w", padx=10)
        self.entry = CTkEntry(self)
        self.entry.grid(column=2, row=0, sticky="ew")
        CTkButton(self, text="Set", width=30, command=self.set).grid(column=3, row=0, sticky="e")

    def set(self):
        value = self.entry.get()
        if not value: return
        self.value = float(value)
        self.entry.delete(0, "end")
        self.value_label.configure(text=value)
        self.on_set(self.value)

    def grid(self, **kwargs):
        kwargs['padx'] = 10
        kwargs['pady'] = 10
        super().grid(**kwargs)

"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkEntry, CTkFrame, CTk
from typing import Callable, Any


class AdvancedEntry(CTkEntry):
    def __init__(self, parent: CTkFrame | CTk, on_enter: Callable[[str], Any], **kwargs):
        super().__init__(parent, **kwargs)
        self._on_enter = on_enter or (lambda: None)
        self.bind("<Return>", lambda _: self._on_enter(self.get()))
        self.bind("<Escape>", lambda _: self.master.focus_set())

    def flash(self, color: str = 'red2'):
        self.configure(fg_color=color)
        self.after(300, lambda: self.configure(fg_color=CTkEntry(None).cget('fg_color'))) # noqa


class EntryWithInstructions(AdvancedEntry):
    def __init__(self, parent: CTkFrame | CTk, on_enter: Callable[[str], None], instructions: str, **kwargs):
        super().__init__(parent, on_enter, **kwargs)
        self.instructions = instructions
        self.fill_instructions()
        self.bind("<FocusOut>", self.fill_instructions)
        self.bind("<FocusIn>", self.clear_instructions)

    def clear_instructions(self, _=None):
        if super().get() != self.instructions: return
        self.delete(0, 'end')
        self.configure(text_color=CTkEntry(None).cget('text_color'))

    def fill_instructions(self, _=None):
        if super().get() != '': return
        self.insert(0, self.instructions)
        self.configure(text_color='gray40')

    def clear(self):
        self.delete(0, 'end')
        self.fill_instructions()

    def get(self):
        val = super().get()
        if val == self.instructions:
            return ''
        return val


class EntryWithInstructionsBlock(CTkFrame):
    def __init__(self, parent, on_enter: Callable[[int, str], Any], instructions: tuple[str, ...], **kwargs):
        padx = kwargs.get('padx', 0)
        del kwargs['padx']
        super().__init__(parent, **kwargs)
        self._on_enter = on_enter
        self.entries = [EntryWithInstructions(self, self.on_enter, t, width=1) for t in instructions]
        for i, e in enumerate(self.entries):
            self.columnconfigure(i*2, weight=1)
            e.grid(column=i*2, row=0, sticky='news')
            if not i == len(self.entries) - 1:
                self.columnconfigure(i*2+1, weight=0, minsize=padx)

    def __iter__(self):
        return iter(self.entries)

    def on_enter(self, _=None):
        for i, e in enumerate(self.entries):
            if e.get() != '':
                self._on_enter(i, e.get())
                break
        self.clear()
        self.master.focus_set()

    def get(self):
        return [e.get() for e in self.entries]

    def set(self, values: tuple[str, ...]):
        if not len(values) == len(self.entries):
            raise ValueError
        for v, e in zip(values, self.entries):
            e.configure(text=v)

    def clear(self):
        for e in self.entries: e.clear()

    def flash(self, index: int = None, color: str = 'red2'):
        if index is None:
            for e in self.entries: e.flash(color)
        else:
            self.entries[index].flash(color)

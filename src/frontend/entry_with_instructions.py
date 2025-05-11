from customtkinter import CTkEntry, CTkFrame


class EntryWithInstructions(CTkEntry):
    def __init__(self, parent, instructions: str, **kwargs):
        super().__init__(parent, **kwargs)
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
    def __init__(self, parent, instructions: tuple[str, ...], width: int, padx: int, **kwargs):
        super().__init__(parent, **kwargs)
        self.entries = [EntryWithInstructions(self, t, width=width) for t in instructions]
        for i, e in enumerate(self.entries): e.grid(column=i, row=0, padx=padx)

    def __iter__(self):
        return iter(self.entries)

    def get(self):
        return [e.get() for e in self.entries]

    def clear(self):
        for e in self.entries: e.clear()

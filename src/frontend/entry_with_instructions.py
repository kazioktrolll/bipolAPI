from customtkinter import CTkEntry


class EntryWithInstructions(CTkEntry):
    def __init__(self, parent, instructions: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.instructions = instructions
        self.fill()
        self.bind("<FocusOut>", self.fill)
        self.bind("<FocusIn>", self.clear)

    def clear(self, _=None):
        try:
            float(self.get())
            return
        except ValueError:
            self.delete(0, 'end')
            self.configure(text_color=CTkEntry(None).cget('text_color'))

    def fill(self, _=None):
        if self.get() != '': return
        self.insert(0, self.instructions)
        self.configure(text_color='gray40')

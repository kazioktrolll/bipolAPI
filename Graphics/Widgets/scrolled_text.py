import customtkinter as ctk


class ScrolledText(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame...
        self.label = ctk.CTkLabel(self, text="")
        self.label.grid(row=0, column=0, padx=20)
        self.label.configure(anchor='w', justify='left')

    def set_text(self, text) -> None:
        self.label.configure(text=text)

    def get_text(self) -> str:
        return self.label.cget("text")

    def insert(self, text) -> None:
        new_text =self.get_text() + text
        self.label.configure(text=new_text)

    def scroll_down(self) -> None:
        self.update_idletasks()
        self._parent_canvas.yview_moveto(1.0)
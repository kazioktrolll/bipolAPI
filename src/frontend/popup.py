from customtkinter import CTkToplevel, CTkFrame


class Popup(CTkToplevel):
    def __init__(self, master: CTkFrame|None):
        super().__init__(master)
        self.overrideredirect(True)
        self.bind("<Escape>", lambda _: self.destroy())

    def run(self):
        self.wm_geometry("")
        self.resizable(False, False)  # Disable resizing
        self.transient()
        self.grab_set()
        self.focus_force()
        def position():
            w = self.winfo_width()
            h = self.winfo_height()
            x = self.winfo_pointerx()
            y = self.winfo_pointery()
            self.geometry(f"{w}x{h}+{x}+{y}")
        self.after(100, position)   # noqa Type-checking is confused with this method
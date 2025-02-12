from customtkinter import CTkToplevel, CTkFrame


class Popup(CTkToplevel):
    def __init__(self, master: CTkFrame|None, title: str = ""):
        super().__init__(master)
        self.title = title
        self.attributes("-toolwindow", True)

    def run(self):
        self.wm_geometry("")
        self.resizable(False, False)  # Disable resizing
        self.transient()
        self.grab_set()
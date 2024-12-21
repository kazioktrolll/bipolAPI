import customtkinter as ctk


class App(ctk.CTk):
    width = 1600
    height = 800

    def __init__(self):
        super().__init__()
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)




    def run(self) -> None:
        self.mainloop()
import customtkinter as ctk
from .top_bar import TopBar


class App(ctk.CTk):
    width = 1600
    height = 800

    def __init__(self):
        super().__init__()
        self.scene = None

        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)
        self.title("Base API Interface")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.top_bar = TopBar(master=self, top_level=self)
        self.top_bar.grid(row=0, column=0, sticky="nsew")


    def run(self) -> None:
        self.mainloop()

    def set_scene(self, scene):
        self.scene = scene
        self.scene.grid(row=1, column=0, sticky="nsew")

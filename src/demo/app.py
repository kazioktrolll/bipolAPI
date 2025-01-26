from customtkinter import CTk
from .scene import Scene


class App:
    def __init__(self):
        self.root = CTk()
        self.root.geometry("1000x600")
        self.root.resizable(False, False)
        self.root.title("Better AVL")

        self.scene = Scene(self.root)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.scene.grid(row=0, column=0, sticky="nsew")

    def run(self):
        self.root.mainloop()
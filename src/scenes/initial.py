from .scene import Scene
from customtkinter import CTkButton


class InitialScene(Scene):
    def build(self) -> None:
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)

        CTkButton(self, text='Load Geometry File', command=self.open_file).grid(row=1, column=1)

    def open_file(self):
        from tkinter import filedialog
        from pathlib import Path
        path = filedialog.askopenfilename(
            title="Select File",
            initialdir=r"C:\Users\kazio\OneDrive\Pulpit\BIPOL",
            filetypes=(("AVL Files", "*.avl"),)
        )
        self.app.geo_path = Path(path)
        from .oper import OperScene
        self.app.set_scene(OperScene(self.app, ['a', 'b', 'c']))
from pathlib import Path


class App:
    def __init__(self):
        from customtkinter import CTk
        from .scenes import Scene
        self.root = CTk()
        self.scene = Scene(self)
        self.geo_path: Path
        self.mass_path: Path
        self.run_path: Path
        self.build()

    def build(self) -> None:
        self.root.geometry("1000x600")
        self.root.resizable(False, False)
        self.root.title("Better AVL")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.scene.grid(row=0, column=0, sticky="nsew")

    def run(self) -> None:
        self.root.mainloop()

    def set_scene(self, scene) -> None:
        from .scenes import Scene
        if not isinstance(scene, Scene): raise TypeError
        self.scene.destroy()
        self.scene = scene
        self.scene.grid(row=0, column=0, sticky="nsew")


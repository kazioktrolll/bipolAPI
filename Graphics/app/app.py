import customtkinter as ctk
from typing import Type
from ..Scenes import Scene


class App(ctk.CTk):
    width = 1600
    height = 800

    def __init__(self):
        super().__init__()
        from .top_bar import TopBar
        from ..handlers import Handler

        self.handlers: dict[str, Handler] = {}
        self.active_scene: Scene = None # noqa

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

    def set_scene(self, scene: Scene):
        self.active_scene = scene
        scene.grid(row=1, column=0, sticky="nsew")

    def change_to_scene(self, scene_type: Type[Scene]):
        self.set_scene(scene_type(self))

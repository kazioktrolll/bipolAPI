from customtkinter import CTk, CTkFrame
from typing import Type
from ..Scenes import Scene


class App(CTk):
    width = 1600
    height = 800

    def __init__(self):
        super().__init__()
        from .top_bar import TopBar
        from .side_bar import SideBar
        from ..handlers import Avl_handler, Xfoil_handler

        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)
        self.title("Base API Interface")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.top_bar = TopBar(master=self, top_level=self)
        self.show_top_bar()

        self.main_frame = CTkFrame(master=self)
        self.main_frame.columnconfigure(0, weight=0)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.grid(row=1, column=0, sticky="nsew")

        self.side_bar = SideBar(master=self.main_frame)
        self.side_bar.grid(row=0, column=0, sticky="nsew")

        self.scene = Scene(None)
        self.avl = Avl_handler(self)
        self.xfoil = Xfoil_handler(self)
        self.side_bar.switch_to_avl()


    def run(self) -> None:
        self.mainloop()

    def set_scene(self, scene: Scene):
        self.scene.deactivate()
        self.scene = scene
        scene.grid(row=0, column=1, sticky="nsew")
        self.scene.activate()

    def change_to_scene(self, scene_type: Type[Scene]):
        self.set_scene(scene_type(self))

    def scene_switch_avl(self):
        self.set_scene(self.avl.scene)

    def scene_switch_xfoil(self):
        self.set_scene(self.xfoil.scene)

    def hide_top_bar(self):
        self.top_bar.grid_remove()

    def show_top_bar(self):
        self.top_bar.grid(row=0, column=0, sticky="nsew")

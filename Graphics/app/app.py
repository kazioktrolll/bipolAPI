import customtkinter as ctk


class App(ctk.CTk):
    width = 1600
    height = 800

    def __init__(self):
        super().__init__()
        from .top_bar import TopBar
        from ..handlers import Handler

        self.handlers: dict[str, Handler] = {}
        self.active_handler: Handler = None # noqa

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

    def update_scene(self):
        scene = self.active_handler.current_scene
        scene.grid(row=1, column=0, sticky="nsew")

from customtkinter import CTkFrame
from ..app import App


class Scene(CTkFrame):
    def __init__(self, app:App):
        super().__init__(app.root)
        self.app = app
        self.build()

    def build(self) -> None: pass

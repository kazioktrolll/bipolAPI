from customtkinter import CTkFrame


class Scene(CTkFrame):
    from ..app import App
    def __init__(self, app:App):
        super().__init__(app.root)
        self.app = app
        self.build()

    def build(self) -> None: pass

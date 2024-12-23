import customtkinter as ctk
from .app import App


class Scene(ctk.CTkFrame):
    """
    A pattern for creating a scene in the application.
    Stage is the actual interactive part of the window, below the menu bar.
    """
    def __init__(self, app: App):
        super().__init__(master=app)


    @property
    def app(self) -> App:
        return self.master  # noqa

    def lift(self):
        super().lift()
        for widget in self.app.winfo_children():
            if widget == self:
                continue
            widget.lift()

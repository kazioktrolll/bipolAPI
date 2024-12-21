import customtkinter as ctk


class Stage(ctk.CTkFrame):
    def __init__(self, app):
        self.app = app
        super().__init__()
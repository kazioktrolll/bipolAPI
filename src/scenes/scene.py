"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame
from typing import final
from ..app import App


class Scene(CTkFrame):
    """
    A base class for creating and managing application scenes.

    A Scene represents a single state or view of the application's UI.
    For example:
        - The initial Scene displayed when the program starts.
        - A subsequent Scene shown after user interaction, such as pressing a 'Load File' button,
          which transitions the app to a working Scene with different widgets and functionalities.

    Attributes:
        app (App): The application instance.
    """

    def __init__(self, app: App):
        super().__init__(app.root)
        self.app = app
        self.to_update = []
        self.build()

    def build(self) -> None:
        """
        Constructs and arranges the widgets to be displayed in the Scene.
        This method should be overridden in subclasses to define the layout and components for each specific Scene.
        """
        if type(self) is not Scene: raise NotImplementedError

    @final
    def update(self) -> None:
        if not self.winfo_exists():
            return

        for tu in self.to_update:
            tu.update()

    @final
    def bind(self, *args, **kwargs):
        self.app.root.bind(*args, **kwargs)

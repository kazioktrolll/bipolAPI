from __future__ import annotations
import customtkinter as ctk
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..app import App


class Scene(ctk.CTkFrame):
    """
    Represents a Scene widget that inherits from `ctk.CTkFrame`.

    This class serves as the base for constructing a specialized `CTkFrame` widget
    which can be used as a scene in a larger application. It integrates functionality
    to manage its child widgets' stacking order, especially providing an efficient
    way to lift the scene and its children in the hierarchy. This is particularly
    beneficial for applications requiring scene management or view layering.

    :ivar app: Reference to the parent application instance.
    :type app: App
    """
    def __init__(self, app: App|None):
        master = app.main_frame if app else None
        super().__init__(master=master)
        self._app = app
        self.configure(corner_radius=0)


    @property
    def app(self):
        from ..app import App
        if isinstance(self._app, App):
            return self._app

    def lift(self):
        """
        Lifts the current widget to the top of the stacking order and ensures that
        all children of the widget are adjusted in the stacking order accordingly.
        This behavior ensures that all child widgets maintain their relative
        ordering while the current widget is elevated.

        :return: None
        """
        super().lift()
        for widget in self.winfo_children():
            if widget == self:
                continue
            widget.lift()

    def activate(self):
        pass

    def deactivate(self):
        self.grid_forget()

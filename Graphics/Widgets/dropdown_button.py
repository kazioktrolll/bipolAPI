from typing import Callable
import customtkinter as ctk


class DropdownButton(ctk.CTkButton):
    item_height = 30
    def __init__(self, master, top_level, **kwargs):
        super().__init__(master, **kwargs)
        self.top_level = top_level
        self.dropdown = ctk.CTkFrame(top_level)
        self.dropdown.place_forget()
        
        self.configure(command=self._toggle_dropdown)
        
    def _show_dropdown(self):
        button_x = self.winfo_rootx() - self.master.winfo_rootx()
        button_y = self.winfo_rooty() - self.master.winfo_rooty()
        button_height = self.winfo_height()

        self.dropdown.place(x=button_x, y=button_y + button_height)
        
    def _hide_dropdown(self):
        self.dropdown.place_forget()
        
    def _toggle_dropdown(self):
        if self.dropdown.winfo_ismapped():
            self._hide_dropdown()
        else:
            self._show_dropdown()
    
    def set_dropdown_items(self, items: dict[str, Callable[[], None]]):
        self.dropdown.configure(height=len(items) * self.item_height)
        for i, (text, command) in enumerate(items.items()):
            button = ctk.CTkButton(self.dropdown, text=text, command=command)
            button.grid(row=i, column=0, sticky="ew")

        mw = 0
        for button in self.dropdown.winfo_children():
            if button.winfo_width() > mw:
                mw = button.winfo_width()
        self.dropdown.configure(width=mw)
            
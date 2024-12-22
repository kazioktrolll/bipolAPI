from typing import Callable
import customtkinter as ctk


class DropdownButton(ctk.CTkButton):
    item_height = 30
    item_ypad = 0
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
        self.dropdown.lift()
        
    def _hide_dropdown(self):
        self.dropdown.place_forget()
        
    def _toggle_dropdown(self):
        if self.dropdown.winfo_ismapped():
            self._hide_dropdown()
        else:
            self._show_dropdown()
    
    def set_items(self, items: dict[str, Callable[[], None]]):
        height = len(items) * self.item_height + (len(items) + 1) * self.item_ypad
        self.dropdown.configure(height=height)
        for i, (text, command) in enumerate(items.items()):
            button = ctk.CTkButton(self.dropdown, text=text, command=command, height=self.item_height, corner_radius=0)
            button.grid(row=i, column=0, sticky="ew", pady=self.item_ypad)

        mw = 0
        for button in self.dropdown.winfo_children():
            if button.winfo_width() > mw:
                mw = button.winfo_width()
        self.dropdown.configure(width=mw)

    def insert_item(self, text: str, command: Callable[[], None], index:int|None=None):
        new_button = ctk.CTkButton(self.dropdown, text=text, command=command, height=self.item_height, corner_radius=0)
        if index is None:
            new_button.grid(row=len(self.dropdown.winfo_children()), column=0, sticky="ew", pady=self.item_ypad)
            return
        buttons = self.dropdown.winfo_children()
        buttons.insert(index, new_button)
        for i, button in enumerate(buttons):
            button.grid(row=i, column=0, sticky="ew", pady=self.item_ypad)
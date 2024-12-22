import customtkinter as ctk
from ..Widgets import DropdownButton


class TopBar(ctk.CTkFrame):
    def __init__(self, master, top_level):
        super().__init__(master, fg_color="grey50")
        self.top_level = top_level
        file_menu = DropdownButton(self, top_level, text="File")
        file_menu.set_dropdown_items({
            "New": lambda: print("New"),
            "Open": lambda: print("Open"),
            "Save": lambda: print("Save"),
            "Exit": lambda: print("Exit")
        })
        row_stack([file_menu])


def row_stack(widgets: list):
    for i, widget in enumerate(widgets):
        widget.grid(row=0, column=i)


if __name__ == "__main__":
    root = ctk.CTk()
    top_bar = TopBar(root)
    root.mainloop()
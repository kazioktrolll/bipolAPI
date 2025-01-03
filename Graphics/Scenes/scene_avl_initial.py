from .scene import Scene


class SceneAvlInitial(Scene):
    def __init__(self, master):
        from customtkinter import CTkButton

        super().__init__(master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        load_file_button = CTkButton(
            self, text="Load File", command=lambda: print(self.get_file())
        )
        load_file_button.grid(row=0, column=0)

    @staticmethod
    def get_file() -> str|None:
        from ..Utilities import open_file_path_dialog
        return open_file_path_dialog([("AVL Files", "*.avl"),
                               ("All Files", "*.*")])

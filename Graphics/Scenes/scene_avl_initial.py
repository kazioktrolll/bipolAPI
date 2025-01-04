from .scene import Scene


class SceneAvlInitial(Scene):
    def __init__(self, master):
        from customtkinter import CTkButton

        super().__init__(master)
        self.app.hide_top_bar()
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        load_file_button = CTkButton(
            self, text="Load File", command=lambda: self.get_file()
        )
        load_file_button.grid(row=0, column=0, sticky="s")

    def get_file(self) -> None:
        from ..Utilities import open_file_path_dialog
        path = open_file_path_dialog([("AVL Files", "*.avl")])
        if not path:
            return
        from customtkinter import CTkLabel
        filename = path.split("/")[-1]
        CTkLabel(self, text=filename).grid(row=1, column=0, sticky="n")

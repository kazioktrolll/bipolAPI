from .scene import Scene


class SceneGeneralInitial(Scene):
    def __init__(self, master):
        from customtkinter import CTkButton

        super().__init__(master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.open_avl_button = CTkButton(
            self, text="Open AVL", command=self.goto_avl, corner_radius=0
        )
        self.open_avl_button.grid(
            row=0, column=0, sticky="nsew"
        )
        self.open_xfoil_button = CTkButton(
            self, text="Open XFOIL", command=self.goto_xfoil, corner_radius=0
        )
        self.open_xfoil_button.grid(
            row=0, column=1, sticky="nsew"
        )

    def goto_avl(self):
        from .scene_avl_initial import SceneAvlInitial
        self.app.set_scene(SceneAvlInitial(self.app))

    def goto_xfoil(self):
        raise NotImplementedError


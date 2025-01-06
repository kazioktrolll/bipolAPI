from customtkinter import CTkFrame, CTkButton


class SideBar(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=0)

        self.avl_button = CTkButton(
            master=self, text="AVL", command=self.switch_to_avl
        )
        self.avl_button.grid(row=0, column=0, sticky="nsew")
        self.xfoil_button = CTkButton(
            master=self, text="XFOIL", command=self.switch_to_xfoil
        )
        self.xfoil_button.grid(row=1, column=0, sticky="nsew")

        for button in (self.avl_button, self.xfoil_button):
            button.configure(corner_radius=0)
            button.configure(height=100)


        self.configure(fg_color="#4a4a4a")

    @property
    def app(self):
        from .app import App
        if isinstance(self.master.master, App):
            return self.master.master
        raise Exception("SideBar is not a child of App")

    def switch_to_avl(self):
        self.xfoil_button.configure(fg_color=self.avl_button.cget("fg_color"))
        self.avl_button.configure(fg_color=self.avl_button.cget("hover_color"))
        self.avl_button.configure(state="disabled")
        self.xfoil_button.configure(state="active")
        self.app.scene_switch_avl()

    def switch_to_xfoil(self):
        self.avl_button.configure(fg_color=self.xfoil_button.cget("fg_color"))
        self.xfoil_button.configure(fg_color=self.xfoil_button.cget("hover_color"))
        self.xfoil_button.configure(state="disabled")
        self.avl_button.configure(state="active")
        self.app.scene_switch_xfoil()

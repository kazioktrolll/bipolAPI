from .scene import Scene



class SceneAvlOper(Scene):
    def __init__(self, master):
        from ..Widgets import HoverButton
        from customtkinter import CTkButton
        from ..Widgets import ScrolledText

        super().__init__(master)
        self.app.show_top_bar()
        self.avl.read_all()
        self.avl.input_command("OPER")
        console_text = self.avl.read_all()

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=1)

        CTkButton(
            self, text="Display Geometry", command=lambda: self.input_command("G")
        ).grid(row=0, column=0, sticky="nsew")

        self.text_display = ScrolledText(self, text=console_text)
        self.text_display.grid(row=0, column=1, sticky="nsew")

#0.0023265
#0.1786332
    @property
    def avl(self):
        return self.app.avl

    def input_command(self, command):
        self.avl.input_command(command)
        self.text_display.insert(self.avl.read_to_prompt())
        self.text_display.scroll_down()

import time

from .scene import Scene


class SceneAvlOper(Scene):
    def __init__(self, master):
        from ..Widgets import HoverButton
        from customtkinter import CTkButton, CTkFrame
        from ..Widgets import ScrolledText, ChangeValuesMenu

        super().__init__(master)
        self.app.show_top_bar()

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=1)

        left_frame = CTkFrame(self)
        left_frame.grid(row=0, column=0, sticky="nsew")

        CTkButton(
            left_frame, text="Display Geometry", command=self.goto_graphics
        ).grid(row=0, column=0, sticky="nsew")
        ChangeValuesMenu(
            left_frame, ["alfa", "beta", "roll", "pitch", "yaw"], do_on_set_functions=[self.change_parameter] * 5
        ).grid(row=1, column=0, sticky="nsew")
        CTkButton(
            left_frame, text="Read", command=lambda: self.update_text
        ).grid(row=2, column=0, sticky="nsew")

        self.text_display = ScrolledText(self)
        self.text_display.grid(row=0, column=1, sticky="nsew")

        self.input_command("OPER")


    @property
    def avl(self):
        return self.app.avl

    def input_command(self, command) -> None:
        time.sleep(1)
        self.avl.input_command(command)
        self.text_display.insert(command + "\n")
        time.sleep(1)
        self.update_text()

    def update_text(self):
        text = self.avl.read_all()
        self.text_display.insert(text)
        self.text_display.scroll_down()

    def change_parameter(self, name: str, value: float) -> None:
        names = {
            "alfa": "A",
            "beta": "B",
            "roll": "R",
            "pitch": "P",
            "yaw": "Y"
        }
        if name not in names:
            raise ValueError("Invalid parameter name")
        command = f"{names[name]} {names[name]} {value}"
        self.input_command(command)

    def goto_graphics(self):
        #from .toplevel_graphics_avl import ToplevelGraphicsAvl
        self.input_command("G")
        #ToplevelGraphicsAvl(self.app)

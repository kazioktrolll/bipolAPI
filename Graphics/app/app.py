import customtkinter as ctk
from ..Widgets import HoverButton
from ..Widgets import ScrolledText
from .top_bar import TopBar


class App(ctk.CTk):
    width = 1600
    height = 800

    def __init__(self):
        super().__init__()
        self.main = None
        self.scene = None

        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)
        self.title("Base API Interface")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.top_bar = TopBar(master=self, top_level=self)
        self.top_bar.grid(row=0, column=0, sticky="nsew")
        self.scene = trial_scene(self)
        self.scene.grid(row=1, column=0, sticky="nsew")


    def run(self) -> None:
        self.mainloop()


def trial_scene(master: App):
    scene = ctk.CTkFrame(master)
    scene.columnconfigure(0, weight=1)
    scene.rowconfigure(0, weight=1)
    scene.rowconfigure(1, weight=0)

    scene.output_area = ScrolledText(scene)
    scene.output_area.grid(row=0, column=0, sticky="nsew")

    lower_layout = ctk.CTkFrame(scene, height=100)
    lower_layout.grid(row=1, column=0, sticky="nsew")
    scene.command_input_field = ctk.CTkEntry(lower_layout, width=40)
    scene.command_input_field.grid(row=0, column=0)
    HoverButton(
        lower_layout,
        text="Send",
        hover_text="Send current contents of input field as a command to the console.",
        command=lambda:scene.master.main.send_command(scene.command_input_field.get() + "\n")
    ).grid(row=0, column=1)
    HoverButton(
        lower_layout,
        text="Quit",
        hover_text="Quit current console app.",
        command=lambda: scene.master.main.send_command("QUIT\n")
    ).grid(row=0, column=2)
    return scene
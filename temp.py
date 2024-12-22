import customtkinter as ctk
from Graphics import App, HoverButton, ScrolledText


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
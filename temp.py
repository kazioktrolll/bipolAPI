import customtkinter as ctk
from Graphics import App, HoverButton, ScrolledText


class TrialScene(ctk.CTkFrame):
    def __init__(self, master: App):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
    
        self.output_area = ScrolledText(self)
        self.output_area.grid(row=0, column=0, sticky="nsew")
    
        lower_layout = ctk.CTkFrame(self, height=100)
        lower_layout.grid(row=1, column=0, sticky="nsew")
        self.command_input_field = ctk.CTkEntry(lower_layout, width=40)
        self.command_input_field.grid(row=0, column=0)
        HoverButton(
            lower_layout,
            text="Send",
            hover_text="Send current contents of input field as a command to the console.",
            command=lambda:self.master.main.send_command(self.command_input_field.get() + "\n")
        ).grid(row=0, column=1)
        HoverButton(
            lower_layout,
            text="Quit",
            hover_text="Quit current console app.",
            command=lambda: self.master.main.send_command("QUIT\n")
        ).grid(row=0, column=2)
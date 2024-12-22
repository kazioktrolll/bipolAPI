import customtkinter as ctk
from Graphics import App, HoverButton, ScrolledText, Stage
from Graphics import avl, xfoil
import threading


class TrialScene(Stage):
    def __init__(self, master: App):
        super().__init__(master)
        # Set up grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        # Set up console output area
        self.output_area = ScrolledText(self)
        self.output_area.grid(row=0, column=0, sticky="nsew")

        # Set up the buttons at the bottom
        lower_layout = ctk.CTkFrame(self, height=100)
        lower_layout.grid(row=1, column=0, sticky="nsew")
        lower_layout.columnconfigure(0, weight=1)
        lower_layout.columnconfigure(1, weight=0)
        lower_layout.columnconfigure(2, weight=1)
        self.command_input_field = ctk.CTkEntry(lower_layout, width=40)
        self.command_input_field.grid(row=0, column=0, sticky="e")

        HoverButton(
            lower_layout,
            text="Send",
            hover_text="Send current contents of input field as a command to the console.",
            command=lambda:self.send_command(self.command_input_field.get() + "\n")
        ).grid(row=0, column=1)
        HoverButton(
            lower_layout,
            text="Quit",
            hover_text="Quit current console app.",
            command=lambda: self.send_command("QUIT\n")
        ).grid(row=0, column=2, sticky="w")
        print(lower_layout.winfo_width())

        # Start the process
        self.process = avl()
        self.output_thread = threading.Thread(target=self.read_output, daemon=True)
        self.output_thread.start()

        self.app.protocol("WM_DELETE_WINDOW", self.on_close)

    def send_command(self, command):
        """Send a command to the base process."""
        if self.process.poll() is None:  # Check if the process is still running
            self.process.stdin.write(command)
            self.process.stdin.flush()
            self.output_area.insert(command)
        else:
            self.output_area.insert("Base process has terminated.\n")
        self.command_input_field.delete(0, len(self.command_input_field.get()))

    def read_output(self):
        """Continuously read output from the base process."""
        while True:
            char = self.process.stdout.read(1)
            self.output_area.insert(char)
            self.output_area.scroll_down()

    def on_close(self):
        """Handle the close event by terminating the base process."""
        self.process.terminate()
        self.app.destroy()
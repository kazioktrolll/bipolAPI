import subprocess
import threading
from Graphics import HoverButton

import customtkinter as ctk
from handlers import avl_path


xfoil_path = r"D:\Program Files\XFOIL6.99\xfoil.exe"


class BaseAPIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Base API Interface")

        # Start the base program
        self.process = subprocess.Popen(
            avl_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)

        self.output_area = ScrolledText(root)
        self.output_area.grid(row=0, column=0, sticky="nsew")

        lower_layout = ctk.CTkFrame(root, height=100)
        lower_layout.grid(row=1, column=0, sticky="nsew")
        self.command_input_field = ctk.CTkEntry(lower_layout, width=40)
        self.command_input_field.grid(row=0, column=0)
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
        ).grid(row=0, column=2)

        self.output_thread = threading.Thread(target=self.read_output, daemon=True)
        self.output_thread.start()

        self.add_mainloop = threading.Thread(target=self.in_mainloop, daemon=True)
        #self.add_mainloop.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def in_mainloop(self):
        while True:
            pass

    def send_command(self, command):
        """Send a command to the base process."""
        if self.process.poll() is None:  # Check if the process is still running
            self.process.stdin.write(command)
            self.process.stdin.flush()
            self.output_area.insert(command)
        else:
            self.output_area.insert("Base process has terminated.\n")

    def read_output(self):
        """Continuously read output from the base process."""
        while True:
            char = self.process.stdout.read(1)
            self.output_area.insert(char)
            self.output_area.scroll_down()

    def on_close(self):
        """Handle the close event by terminating the base process."""
        self.process.terminate()
        self.root.destroy()


class ScrolledText(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame...
        self.label = ctk.CTkLabel(self)
        self.label.grid(row=0, column=0, padx=20)
        self.label.configure(anchor='w', justify='left')

    def set_text(self, text) -> None:
        self.label.configure(text=text)

    def get_text(self) -> str:
        return self.label.cget("text")

    def insert(self, text) -> None:
        new_text =self.get_text() + text
        self.label.configure(text=new_text)

    def scroll_down(self) -> None:
        self.update_idletasks()
        self._parent_canvas.yview_moveto(1.0)


# Create the base API interface
if __name__ == "__main__":
    from Graphics import App
    tk_root = App()
    app = BaseAPIApp(tk_root)
    tk_root.run()
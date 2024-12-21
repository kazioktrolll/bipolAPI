import subprocess
import customtkinter as ctk


class Handler:
    def __init__(self, path: str):
        self.process = subprocess.Popen(
            path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    def input_command(self, command: str) -> None:
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    def on_close(self) -> None:
        self.process.terminate()


class Scene(ctk.CTkFrame):
    ...
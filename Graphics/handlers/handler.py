import subprocess
import customtkinter as ctk
from ..scene import Scene


def open_process(path: str) -> subprocess.Popen:
    return subprocess.Popen(
            path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )


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
        self.main_scene: Scene
        self.current_scene: Scene

    def input_command(self, command: str) -> None:
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    def on_close(self) -> None:
        self.process.terminate()

    def set_scene(self, scene):
        self.scene = scene
        self.scene.grid(row=1, column=0, sticky="nsew")

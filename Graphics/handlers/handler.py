import subprocess
import customtkinter as ctk
from ..app import App


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
    def __init__(self, master:App, path: str):
        from ..scene import Scene

        self.master = master
        self.process = subprocess.Popen(
            path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.main_scene: Scene = None   # noqa
        self.current_scene: Scene = None    # noqa

    @property
    def app(self) -> App:
        return self.master

    def input_command(self, command: str) -> None:
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    def on_close(self) -> None:
        self.process.terminate()

    def set_scene(self, scene):
        self.current_scene = scene
        self.app.update_scene()

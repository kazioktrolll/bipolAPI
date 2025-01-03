import subprocess
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
    """
    Encapsulates the handling of a subprocess in conjunction with an application.

    Provides methods to interact with a subprocess via standard input and
    manage its lifecycle, including initialization and termination. This class
    is designed to interface subprocesses with the provided application for
    streamlined execution and communication.

    :ivar master: Instance of the main application interacting with the subprocess.
    :type master: App
    :ivar process: Subprocess object managing the external process.
    :type process: subprocess.Popen
    """
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

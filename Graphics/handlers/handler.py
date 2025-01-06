import subprocess
from ..app import App
import threading
import queue
import time
from abc import ABC, abstractmethod


def open_process(path: str) -> subprocess.Popen:
    return subprocess.Popen(
            path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )


class Handler(ABC):
    """
    Encapsulates the handling of a subprocess in conjunction with an application.

    Provides methods to interact with a subprocess via standard input and
    manage its lifecycle, including initialization and termination. This class
    is designed to interface subprocesses with the provided application for
    streamlined execution and communication.

    :ivar process: Subprocess object managing the external process.
    :type process: subprocess.Popen
    :ivar scene: Scene object associated with the subprocess.
    :type scene: Scene
    """
    @abstractmethod
    def __init__(self, path: str):
        from .. import Scene

        self.process = subprocess.Popen(
            path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.scene = Scene(None)


    def input_command(self, command: str) -> None:
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    def read_to_prompt(self) -> str:
        _r = ""
        while True:
            c = self.process.stdout.read(1)
            _r += c
            if _r[-2:] == "c>":
                break
        return _r

    def threaded_reader(self, data_queue: queue.Queue):
        """
        Continuously reads from the buffer and puts data into the queue.
        """
        while True:
            chunk = self.process.stdout.read(1)
            if chunk:
                data_queue.put(chunk)

    def read_all(self, timeout=0.2):
        """
        Reads all data from the buffer using a thread to avoid blocking.
        Stops reading if no new data is received within `timeout` seconds.

        Returns:
            str: The concatenated data read from the buffer.
        """
        data_queue = queue.Queue()
        reader_thread = threading.Thread(target=self.threaded_reader, args=[data_queue])
        reader_thread.daemon = True  # Ensure the thread exits with the main program
        reader_thread.start()

        data = []
        start_time = time.time()

        while True:
            try:
                # Wait for data in the queue with a timeout
                chunk = data_queue.get(timeout=timeout)
                data.append(chunk)
                start_time = time.time()  # Reset the timer
            except queue.Empty:
                # Timeout reached without new data
                if time.time() - start_time > timeout:
                    break
        return ''.join(data)

    def on_close(self) -> None:
        self.process.terminate()

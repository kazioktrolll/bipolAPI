from subprocess import Popen, PIPE, TimeoutExpired


avl_exe_path = r"C:\Users\kazio\PycharmProjects\bipolAPI\src\avl\avl.exe"


class PlotWindow:
    def __init__(self, file: str, command: str):
        self.process = Popen([avl_exe_path, file], stdin=PIPE, text=True)
        self.process.stdin.write(command)
        self.process.stdin.flush()

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except TimeoutExpired:
            self.process.kill()
            self.process.wait()

        self.process.stdin.close()


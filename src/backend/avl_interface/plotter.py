from subprocess import Popen, PIPE, TimeoutExpired
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from .avl_interface import avl_exe_path, AVLInterface
from ..geo_design import Geometry


class PlotWindow:
    def __init__(self, file_path: str | Path, command: str):
        file_path = Path(file_path)
        self.process = Popen([avl_exe_path, file_path], stdin=PIPE, text=True)
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

    @classmethod
    def plot_trefftz(cls, geometry: Geometry, run_file_data: dict[str, list[float]], case_number: int = 1):
        contents = AVLInterface.create_run_file_contents(geometry, run_file_data)
        temp_dir = TemporaryDirectory(prefix='gavl_')
        temp_dir_path = Path(temp_dir.name)

        avl_file_path = temp_dir_path.joinpath('plane.avl')
        run_file_path = temp_dir_path.joinpath('plane.run')
        with open(avl_file_path, 'w') as avl_file: avl_file.write(geometry.string())
        with open(run_file_path, 'w') as run_file: run_file.write(contents)

        command = f'OPER\n{case_number}\nX\nT\n'
        pw = cls(avl_file_path, command)
        sleep(.5)
        temp_dir.cleanup()
        return pw

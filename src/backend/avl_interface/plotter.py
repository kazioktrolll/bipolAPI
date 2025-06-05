"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from subprocess import Popen, PIPE, TimeoutExpired, run
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from .avl_interface import avl_exe_path, AVLInterface
from ..geo_design import Geometry


class PlotWindow:
    def __init__(self, file_path: str | Path, command: str, cwd: str | Path):
        self.process = Popen([avl_exe_path, file_path], stdin=PIPE, text=True, cwd=cwd)
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
    def plot_trefftz(cls, geometry: Geometry, run_file_data: dict[str, list[float]], cwd: str | Path, case_number: int = 1):
        contents = AVLInterface.create_run_file_contents(geometry, run_file_data)
        temp_dir = TemporaryDirectory(prefix='gavl_')
        temp_dir_path = Path(temp_dir.name)

        avl_file_path = temp_dir_path.joinpath('plane.avl')
        run_file_path = temp_dir_path.joinpath('plane.run')
        with open(avl_file_path, 'w') as avl_file: avl_file.write(geometry.string())
        with open(run_file_path, 'w') as run_file: run_file.write(contents)

        command = f'OPER\n{case_number}\nX\nT\nH\n\n\nQ\n'
        pw = cls(avl_file_path, command, cwd)
        sleep(.5)
        temp_dir.cleanup()
        return pw

    @classmethod
    def ps2png(cls, ps_path: str | Path, png_path: str | Path, add_background: bool = True):
        """Converts the given PostScript file to a PNG file."""
        run([
            "gswin32c",  # Or "gswin32c" if you're using 32-bit
            "-dSAFER", "-dBATCH", "-dNOPAUSE",
            f"-sDEVICE={"png16m" if add_background else "pngalpha"}",
            "-r300",
            f"-sOutputFile={png_path}",
            ps_path
        ], check=True)

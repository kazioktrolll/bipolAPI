"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from ..geo_design import Geometry
from pathlib import Path
from tempfile import TemporaryDirectory
from .results_parser import ResultsParser

val_dict = dict[str, float]
avl_exe_path = Path(__file__).parent.parent.parent / 'avl' / 'avl.exe'


class AVLInterface:
    @classmethod
    def create_run_file_contents(cls, geometry: Geometry, run_file_data: dict[str, list[float]]) -> str:
        """Returns a string containing the input data transformed into a .run format."""
        no_of_runs = len(list(run_file_data.values())[0])
        _r = ''
        for i in range(no_of_runs):
            _r += f"Run case  {i + 1}: AutoGenCase{i}\n"
            _r += '\n'.join([f"{names} = {value[i]}" for names, value in run_file_data.items()])
            _r += '\n\n'

        _r += ('grav.acc. = 9.80665 m/s^2\n'
               'density = 1.225 kg/m^3\n')
        return _r

    @classmethod
    def create_st_command(cls, paths: list[Path]) -> str:
        """Creates a command string for running a given number of cases, each run 'ST' and saved to file."""
        _r = 'OPER\n'
        for i, path in enumerate(paths):
            _r += f'{i + 1}\nX\nst\n'
            _r += str(path.absolute())
            _r += '\n'
        return _r

    @classmethod
    def execute(cls, command: str, avl_file_path) -> str:
        from subprocess import Popen, PIPE
        avl = Popen([avl_exe_path, str(avl_file_path)], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        dump = avl.communicate(bytes(command, encoding='utf-8'), timeout=None)[0].decode()
        return dump

    @classmethod
    def create_temp_files(cls, temp_dir: Path, nof_cases: int) -> list[Path]:
        path = temp_dir.joinpath('st_files')
        path.mkdir()
        files = [path.joinpath(f'{i + 1}') for i in range(nof_cases)]
        return files

    @classmethod
    def run_series(cls, geometry: Geometry, data: dict[str, list[float]], flag: 'AbortFlag') -> tuple[list[list[val_dict]], str]:
        """
        Runs all cases using 'ST' and returns the results.

        Return:
            [[{name-value} for intro, forces, ST] for each case]
        """
        if flag: return [], 'Aborted'
        nof_cases = len(list(data.values())[0])
        contents = cls.create_run_file_contents(geometry, data)
        temp_dir = TemporaryDirectory(prefix='gavl_')
        temp_dir_path = Path(temp_dir.name)

        files = cls.create_temp_files(temp_dir_path, nof_cases)

        avl_file_path = temp_dir_path / 'plane.avl'
        run_file_path = temp_dir_path / 'plane.run'
        with open(avl_file_path, 'w') as avl_file:
            avl_file.write(geometry.string())
        with open(run_file_path, 'w') as run_file:
            run_file.write(contents)
        if not flag:
            command = cls.create_st_command(files)
            dump = cls.execute(command, avl_file_path)
        if not flag:
            errors = ResultsParser.loading_issues_from_dump(dump)
            vals = ResultsParser.all_sts_to_data(files)
        else:
            errors = 'Aborted'
            vals = []

        temp_dir.cleanup()
        return vals, errors


class AbortFlag:
    """A simple object passed along the process thread to monitor if the process should be aborted."""

    def __init__(self):
        self._aborted = False

    def abort(self):
        self._aborted = True

    def __bool__(self):
        return self._aborted

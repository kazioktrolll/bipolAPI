"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from pathlib import Path
import shutil
from subprocess import Popen, PIPE
from .results_parser import ResultsParser
from .. import physics
from ..geo_design import Geometry

val_dict = dict[str, float]
avl_exe_path = Path(__file__).parent.parent.parent / 'avl' / 'avl.exe'


class AVLInterface:
    @classmethod
    def create_run_file_contents(cls, run_file_data: dict[str, list[float]], height: float) -> str:
        """Returns a string containing the input data transformed into a .run format."""
        no_of_runs = len(list(run_file_data.values())[0])
        _r = ''
        for i in range(no_of_runs):
            _r += f"Run case  {i + 1}: AutoGenCase{i}\n"
            _r += '\n'.join([f"{names} = {value[i]}" for names, value in run_file_data.items()])
            _r += '\n\n'

        _r += ('grav.acc. = 9.80665 m/s^2\n'
               f'density = {physics.get_density(height)} kg/m^3\n')
        return _r

    @classmethod
    def create_st_command(cls, paths: list[Path]) -> str:
        """Creates a command string for running a given number of cases, each run 'ST' and saved to file."""
        _r = 'OPER\n'
        for i, path in enumerate(paths):
            _r += (f'{i + 1}\n'
                   f'X\n'
                   f'st\n'
                   f'{str(path.absolute())}\n')
        _r += ('\n'
               'Q\n')
        return _r

    @classmethod
    def execute(cls, command: str, avl_file_path, app_wd: Path) -> str:
        avl = Popen([avl_exe_path, str(avl_file_path)], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True, cwd=app_wd)
        dump, err = avl.communicate(bytes(command, encoding='utf-8'), timeout=None)
        dump = dump.decode()
        err = err.decode()
        err = err.replace('Note: The following floating-point exceptions are signalling: IEEE_DIVIDE_BY_ZERO\n', '')
        # This message happens sometimes, no idea why, doesn't seem to affect anything, so I just ignore it
        if err:
            raise RuntimeError(err)
        if '***' in dump:
            err_line = [line for line in dump.split('\n') if '***' in line]
            raise RuntimeError('\n'.join(err_line))
        if 'SINVRT' in dump:
            raise RuntimeError('SINVRT - geometry too complex')
        if 'SDUPL' in dump:
            raise RuntimeError('SDUPL - geometry resolution too high')
        return dump

    @classmethod
    def create_temp_files(cls, temp_dir: Path, nof_cases: int) -> list[Path]:
        path = temp_dir.joinpath('st_files')
        path.mkdir()
        files = [path.joinpath(f'{i + 1}') for i in range(nof_cases)]
        return files

    @classmethod
    def run_series(cls,
                   geometry: Geometry,
                   data: dict[str, list[float]],
                   height: float,
                   flag: 'AbortFlag',
                   app_work_dir: Path) -> tuple[list[list[val_dict]], str]:
        """
        Runs all cases using 'ST' and returns the results.

        Return:
            [[{name-value} for intro, forces, ST] for each case]
        """
        if flag: return [], 'Aborted'
        nof_cases = len(list(data.values())[0])
        contents = cls.create_run_file_contents(data, height)
        i = 0
        while True:
            try:
                work_dir = app_work_dir / f'series_{i}'
                work_dir.mkdir()
                break
            except FileExistsError:
                i += 1

        files = cls.create_temp_files(work_dir, nof_cases)

        avl_file_path = work_dir / 'plane.avl'
        run_file_path = work_dir / 'plane.run'
        with open(avl_file_path, 'w') as avl_file:
            avl_file.write(geometry.string())
        with open(run_file_path, 'w') as run_file:
            run_file.write(contents)
        if not flag:
            command = cls.create_st_command(files)
            dump = cls.execute(command, avl_file_path, app_work_dir)
        if not flag:
            errors = ResultsParser.loading_issues_from_dump(dump)
            vals = ResultsParser.all_sts_to_data(files)
        else:
            errors = 'Aborted'
            vals = []

        shutil.rmtree(work_dir)
        return vals, errors


class AbortFlag:
    """A simple object passed along the process thread to monitor if the process should be aborted."""

    def __init__(self):
        self._aborted = False

    def abort(self):
        self._aborted = True

    def __bool__(self):
        return self._aborted

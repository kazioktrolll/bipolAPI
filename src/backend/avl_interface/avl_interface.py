"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import shutil
from pathlib import Path
from subprocess import Popen, PIPE
import logging

from .results_parser import ResultsParser
from .. import physics
from ..geo_design import Geometry

val_dict = dict[str, float]
avl_exe_path = Path(__file__).parent.parent.parent / 'avl' / 'avl.exe'


class AVLInterface:
    """A toolbox class to act as the AVL interface.
    Also contains all methods required to format data into AVL's formats, etc."""

    @staticmethod
    def create_run_file_contents(run_file_data: dict[str, list[float]], height: float) -> str:
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

    @staticmethod
    def create_st_command(paths: list[Path]) -> str:
        """Creates a command string for running a given number of cases, each runs 'ST' and saved to file."""
        _r = 'OPER\n'
        for i, path in enumerate(paths):
            _r += (f'{i + 1}\n'
                   f'X\n'
                   f'st\n'
                   f'{str(path.absolute())}\n')
        _r += ('\n'
               'Q\n')
        return _r

    @staticmethod
    def execute(command: str, avl_file_path: Path | str, app_wd: Path) -> str:
        """
        Executes the given AVL command or chain of commands, returns the full AVL output as string.

        Creates a new ``Popen`` instance of AVL, using stdin ``PIPE`` feeds the instance the given command,
        and returns the full stdout ``PIPE`` output as a string.
        If any errors are encountered, a respective exception will be raised, except for ``SINVRT``.

        Parameters:
            command (str): The command to be executed. For a chain of commands, join them using \\n.
            avl_file_path (Path, str): Path to the .avl file to run the AVL on.
            app_wd (Path): Path to the application working directory, where the AVL should be run from.
              Any files created directly by AVL will be saved there.
        Returns:
            str: The full AVL output as string.
        Raises:
            Exception: If an error occurs while executing the command.
        """
        logging.debug(f'Executing AVL command: {command.replace('\n', ' // ')}')
        avl = Popen([avl_exe_path, str(avl_file_path)], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True, cwd=app_wd)
        if command[-2:] != '\n': command += '\n'
        dump, err = avl.communicate(bytes(command, encoding='utf-8'))
        dump = dump.decode()
        err = err.decode()
        if err:
            # Ignore 'Notes' - non-critical notifications
            err = '\n'.join([line for line in err.split('\n') if 'Note' not in line])
            if err: raise RuntimeError(err)
        if '***' in dump:
            err_line = [line for line in dump.split('\n') if '***' in line]
            raise RuntimeError('\n'.join(err_line))
        if 'SINVRT' in dump:
            pass
            # raise RuntimeError('SINVRT - geometry too complex, cannot construct a spline.')
        if 'SDUPL' in dump:
            raise RuntimeError('SDUPL - geometry resolution too high, decrease mesh density.')
        return dump

    @staticmethod
    def create_temp_files(temp_dir: Path, nof_cases: int) -> list[Path]:
        """Returns a list of empty temporary files."""
        logging.debug(f'Creating {nof_cases} temporary files at {temp_dir.name}.')
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

        Parameters:
            geometry (Geometry): The geometry to turn into .avl file.
            data (dict[str, list[float]): The data to turn into a .run file.
            height (float): The flight altitude, in meters.
            flag (AbortFlag): The Flag object to abort mid-execution, in case the user cancels the calculation.
            app_work_dir (Path): The application working directory, where the AVL should be run from.

        Return:
            ([[{name-value} for intro, forces, ST] for each case], errors)
        """
        if flag: return [], 'Aborted'  # If the user cancelled the calculation mid-execution. Will be checked multiple times.
        nof_cases = len(list(data.values())[0])
        logging.info(f'Running {nof_cases} cases.')
        contents = cls.create_run_file_contents(data, height)
        # Create a new directory for this run, at the first not-used name.
        i = 0
        while True:
            try:
                work_dir = app_work_dir / f'series_{i}'
                work_dir.mkdir()
                break
            except FileExistsError:
                i += 1
        logging.debug(f'Created temporary directory for series: {work_dir.name}')
        # Create the required empty files
        files = cls.create_temp_files(work_dir, nof_cases)
        avl_file_path = work_dir / 'plane.avl'
        run_file_path = work_dir / 'plane.run'
        # Fill the files with data
        with open(avl_file_path, 'w') as avl_file:
            avl_file.write(geometry.string())
        with open(run_file_path, 'w') as run_file:
            run_file.write(contents)
        # Create the command to execute the series of measurements and run it
        if not flag:
            command = cls.create_st_command(files)
            dump = cls.execute(command, avl_file_path, app_work_dir)
            logging.info('Finished running series.')
        # Parse data and potential errors
        if not flag:
            errors = ResultsParser.loading_issues_from_dump(dump)  # noqa The dump is not referenced before assignment, as flag is irreversible.
            if errors: logging.warning(f'Running series resulted in errors: {errors}')
            else: logging.info('No errors found.')
            vals = ResultsParser.all_sts_to_data(files)
        else:
            errors = 'Aborted'
            vals = []
        # Delete the working directory of this series
        shutil.rmtree(work_dir)
        # Return data, errors
        return vals, errors


class AbortFlag:
    """A simple object passed along the process thread to monitor if the process should be aborted."""

    def __init__(self):
        self._aborted = False

    def abort(self):
        logging.warning('Abort flag raised.')
        self._aborted = True

    def __bool__(self):
        return self._aborted

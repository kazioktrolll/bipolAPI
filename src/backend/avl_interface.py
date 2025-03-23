from .geo_design import Geometry
from pathlib import Path
from tempfile import TemporaryDirectory
import re


avl_path = Path(r"C:\Users\kazio\PycharmProjects\bipolAPI\src\avl\avl.exe")
local_path = Path(r"C:\Users\kazio\PycharmProjects\bipolAPI\src\temp_files_dir")
st_path = local_path.joinpath("st_files")


class AVLInterface:
    def __init__(self, geometry: Geometry) -> None:
        self.geometry = geometry

    @classmethod
    def write_to_avl_file(cls, contents: str) -> None:
        """Writes the input contents to a designated .avl file used for running cases."""
        with open(local_path.joinpath('local.avl'), 'w') as avl_file: avl_file.write(contents)

    @classmethod
    def write_to_run_file(cls, contents: str) -> None:
        """Writes the input contents to a designated .run file used for running cases."""
        with open(local_path.joinpath('local.run'), 'w') as run_file: run_file.write(contents)

    @classmethod
    def create_run_file_contents(cls, geometry: Geometry, run_file_data: dict[str, list[float]]) -> str:
        """Returns a string containing the input data transformed into a .run format."""
        no_of_runs = len(list(run_file_data.values())[0])
        _r = ''
        for i in range(no_of_runs):
            _r += (f"Run case  {i+1}: AutoGenCase{i}\n"
                  f"X_cg = {geometry.ref_pos.x}\n")
            _r += '\n'.join([f"{names} = {value[i]}" for names, value in run_file_data.items()])
            _r += '\n\n'
        return _r

    @classmethod
    def create_st_command(cls, paths: list[Path]) -> str:
        """Creates a command string for running a given number of cases, each run 'ST' and saved to file."""
        _r = 'OPER\n'
        for i, path in enumerate(paths):
            _r += f'{i+1}\nX\nst\n'
            _r += str(path.absolute())
            _r += '\n'
        return _r

    @classmethod
    def execute(cls, command: str) -> str:
        from subprocess import Popen, PIPE
        avl = Popen([avl_path, str(local_path.joinpath('local.avl'))], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        dump = avl.communicate(bytes(command, encoding='utf-8'),
                               timeout=1)[0].decode()
        return dump

    @classmethod
    def create_temp_files(cls, nof_cases: int) -> tuple[TemporaryDirectory, list[Path]]:
        temp_dir = TemporaryDirectory(prefix='gavl_')
        dir_path = Path(temp_dir.name)
        files = [dir_path.joinpath(f'{i+1}') for i in range(nof_cases)]
        return temp_dir, files

    @classmethod
    def run_series(cls, geometry: Geometry, data: dict[str, list[float]]) -> list[list[dict[str, float]]]:
        """
        Runs all cases using 'ST' and returns the results.

        Return:
            [[{name-value} for intro, forces, ST] for each case]
        """
        nof_cases = len(list(data.values())[0])
        contents = AVLInterface.create_run_file_contents(geometry, data)
        temp_dir, files = cls.create_temp_files(nof_cases)
        cls.write_to_run_file(contents)
        cls.write_to_avl_file(geometry.string())
        command = cls.create_st_command(files)
        cls.execute(command)
        vals = ResultsParser.all_sts_to_data(files)
        temp_dir.cleanup()
        return vals


class ResultsParser:
    @classmethod
    def _split_dump(cls, dump: str) -> list[str]:
        """Splits the dump string on === lines."""
        dump = re.split(r'=+\r\n', dump)
        return dump

    @classmethod
    def loading_issues_from_dump(cls, dump: str) -> str:
        """Returns the issue part of the dump."""
        return cls._split_dump(dump)[2]

    @classmethod
    def chop_results(cls, dump: str) -> list[str]:
        """Returns the relevant part from the input 'forces' string."""
        dump = re.split(r'-{61,}', dump)
        return [block for block in dump if 'Vortex Lattice Output' in block]

    @classmethod
    def forces_to_dict(cls, forces_str: str) -> dict[str, float]:
        """Takes the chopped 'forces' string and converts it to a name-value dict."""
        vals = re.sub(r'\s+=\s+', '=', forces_str)
        vals = re.sub(r'\r\n', '', vals)
        vals = vals.split()
        _r: dict[str, float] = {}
        for line in vals:
            if not '=' in line: continue
            key, value = line.split('=')
            _r[key] = float(value)
        return _r

    @classmethod
    def st_file_to_dict(cls, st_str: str) -> dict[str, float]:
        """Takes the raw contents of the 'ST' file and converts it to a name-value dict."""
        st_str = re.sub(r'\s+=\s+', '=', st_str)
        st_str = re.sub(r'\n', '', st_str)
        st_str = re.sub(r'Clb Cnr / Clr Cnb', 'Clb_Cnr/Clr_Cnb', st_str)
        vals = st_str.split()
        _r: dict[str, float] = {}
        for val in vals:
            if not '=' in val: continue
            k, v = val.split('=')
            _r[k] = float(v)
        return _r

    @classmethod
    def split_st_dict(cls, st_dict: dict[str, float]) -> list[dict[str, float]]:
        """Splits the 'ST_file' dict into 'forces' and 'ST' """
        breakpoints = ['Alpha', 'CLa']
        result = []
        current_dict = {}

        for key, value in st_dict.items():
            if key in breakpoints and current_dict:
                result.append(current_dict)
                current_dict = {}
            current_dict[key] = value

        if current_dict:
            result.append(current_dict)  # Append the last chunk

        return result[1:]

    @classmethod
    def all_sts_to_data(cls, paths: list[Path]) -> list[list[dict[str, float]]]:
        """Converts every file in the 'ST' directory and converts it to a dict."""
        _r = []
        for path in paths:
            with open(path) as f: data = f.read()
            data = cls.st_file_to_dict(data)
            data = cls.split_st_dict(data)
            data[1] = cls.sort_st_dict(data[1])
            _r.append(data)
        return _r

    @classmethod
    def sort_st_dict(cls, st_dict: dict[str, float], join=True) -> dict[str, dict[str, float]] | dict[str, float]:
        """Sorts the dict so that relevant values are next to each other."""
        Xnp = st_dict.pop('Xnp')
        try: ClbCnr = st_dict.pop('Clb_Cnr/Clr_Cnb')
        except KeyError: ClbCnr = 0
        dicts: dict[str, dict[str, float]] = {}
        for k, v in st_dict.items():
            category = k[-2:] if k[-2] == 'd' else k[-1:]
            if category not in dicts: dicts[category] = {}
            dicts[category][k] = v

        dicts['misc'] = {'Xnp': Xnp, 'Clb_Cnr/Clr_Cnb': ClbCnr}
        if join: return {k: v for d in dicts.values() for k, v in d.items()}
        return dicts

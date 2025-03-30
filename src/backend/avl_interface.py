from .geo_design import Geometry
from pathlib import Path
from tempfile import TemporaryDirectory
import re


val_dict = dict[str, float]
avl_exe_path = Path(r"C:\Users\kazio\PycharmProjects\bipolAPI\src\avl\avl.exe")


class AVLInterface:
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

        _r += ('grav.acc. = 9.80665 m/s^2\n'
              'density = 1.2250122659906943 kg/m^3\n')
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
    def execute(cls, command: str, avl_file_path) -> str:
        from subprocess import Popen, PIPE
        avl = Popen([avl_exe_path, str(avl_file_path)], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        dump = avl.communicate(bytes(command, encoding='utf-8'),
                               timeout=1)[0].decode()
        return dump

    @classmethod
    def create_temp_files(cls, temp_dir: Path, nof_cases: int) -> list[Path]:
        path = temp_dir.joinpath('st_files')
        path.mkdir()
        files = [path.joinpath(f'{i+1}') for i in range(nof_cases)]
        return files

    @classmethod
    def run_series(cls, geometry: Geometry, data: dict[str, list[float]]) -> tuple[list[list[val_dict]], str]:
        """
        Runs all cases using 'ST' and returns the results.

        Return:
            [[{name-value} for intro, forces, ST] for each case]
        """
        nof_cases = len(list(data.values())[0])
        contents = cls.create_run_file_contents(geometry, data)
        temp_dir = TemporaryDirectory(prefix='gavl_')
        temp_dir_path = Path(temp_dir.name)

        files = cls.create_temp_files(temp_dir_path, nof_cases)

        avl_file_path = temp_dir_path.joinpath('plane.avl')
        run_file_path = temp_dir_path.joinpath('plane.run')
        with open(avl_file_path, 'w') as avl_file: avl_file.write(geometry.string())
        with open(run_file_path, 'w') as run_file: run_file.write(contents)

        command = cls.create_st_command(files)
        dump = cls.execute(command, avl_file_path)
        errors = ResultsParser.loading_issues_from_dump(dump)

        vals = ResultsParser.all_sts_to_data(files)

        temp_dir.cleanup()
        return vals, errors


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
    def forces_to_dict(cls, forces_str: str) -> val_dict:
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
    def st_file_to_dict(cls, st_str: str) -> val_dict:
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
    def split_st_dict(cls, st_dict: val_dict) -> list[val_dict]:
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
    def all_sts_to_data(cls, paths: list[Path]) -> list[list[val_dict]]:
        """Converts every file in the 'ST' directory and converts it to a dict."""
        _r = []
        for path in paths:
            with open(path) as f: data = f.read()
            data = cls.st_file_to_dict(data)
            data = cls.split_st_dict(data)
            data[0] = cls.sort_forces_dict(data[0])
            data[1] = cls.sort_st_dict(data[1])
            _r.append(data)
        return _r

    @classmethod
    def sort_forces_dict(cls, forces_dict: val_dict, join=True) -> val_dict | list[val_dict]:
        sorted_keys = (
            ('Alpha', 'Beta', 'Mach'),
            ('pb/2V', 'qc/2V', 'rb/2V'),
            ("p'b/2V", "r'b/2V"),
            ('CXtot', 'CYtot', 'CZtot'),
            ('Cltot', 'Cmtot', 'Cntot'),
            ("Cl'tot", "Cn'tot"),
            ('CLtot', 'CDtot', 'CDvis', 'CLff', 'CYff'),
            ('CDind', 'CDff', 'e')
        )

        sorted_dicts = []
        for group in sorted_keys:
            sorted_dicts.append({})
            for key in group: sorted_dicts[-1][key] = forces_dict.pop(key)
        sorted_dicts.append(forces_dict)

        if join: return {k: v for d in sorted_dicts for k, v in d.items()}
        return sorted_dicts

    @classmethod
    def sort_st_dict(cls, st_dict: val_dict, join=True) -> dict[str, val_dict] | val_dict:
        """Sorts the dict so that relevant values are next to each other."""
        Xnp = st_dict.pop('Xnp')
        try: ClbCnr = st_dict.pop('Clb_Cnr/Clr_Cnb')
        except KeyError: ClbCnr = 0
        dicts: dict[str, val_dict] = {}
        for k, v in st_dict.items():
            category = k[-2:] if k[-2] == 'd' else k[-1:]
            if category not in dicts: dicts[category] = {}
            dicts[category][k] = v

        dicts['misc'] = {'Xnp': Xnp, 'Clb_Cnr/Clr_Cnb': ClbCnr}
        if join: return {k: v for d in dicts.values() for k, v in d.items()}
        return dicts

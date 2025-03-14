from .geo_design import Geometry
from pathlib import Path


avl_path = Path(r"C:\Users\kazio\PycharmProjects\bipolAPI\src\avl\avl.exe")
local_path = Path(r"C:\Users\kazio\PycharmProjects\bipolAPI\src\temp_files_dir")


class AVLInterface:
    def __init__(self, geometry: Geometry) -> None:
        self.geometry = geometry

    @classmethod
    def write_to_avl_file(cls, contents: str) -> None:
        with open(local_path.joinpath('local.avl'), 'w') as avl_file: avl_file.write(contents)

    @classmethod
    def write_to_run_file(cls, contents: str) -> None:
        with open(local_path.joinpath('local.run'), 'w') as run_file: run_file.write(contents)

    @classmethod
    def create_run_file_contents(cls, geometry: Geometry, run_file_data: dict[str, list[float]]) -> str:
        no_of_runs = len(list(run_file_data.values())[0])
        _r = ''
        for i in range(no_of_runs):
            _r += (f"Run case  {i+1}: AutoGenCase{i}\n"
                  f"X_cg = {geometry.ref_pos.x}\n")
            _r += '\n'.join([f"{names} = {value[i]}" for names, value in run_file_data.items()])
            _r += '\n\n'
        return _r

    @classmethod
    def create_st_command(cls, nof_cases: int) -> str:
        _r = 'OPER\n'
        for i in range(1, nof_cases+1):
            _r += f'{i}\nX\nst\n'
            _r += rf'C:\Users\kazio\PycharmProjects\bipolAPI\src\temp_files_dir\st_files\{i}.txt'
            _r += '\n'
        return _r

    @classmethod
    def execute_case(cls, geometry: Geometry, run_file_contents: str) -> str:
        cls.write_to_avl_file(geometry.string())
        cls.write_to_run_file(run_file_contents)
        return cls.execute(command = 'OPER\nXX\n')

    @classmethod
    def execute(cls, command: str) -> str:
        from subprocess import Popen, PIPE
        avl = Popen([avl_path, str(local_path.joinpath('local.avl'))], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        dump = avl.communicate(bytes(command, encoding='utf-8'),
                               timeout=1)[0].decode()
        return dump

    @classmethod
    def _split_dump(cls, dump: str) -> list[str]:
        import re
        dump = re.split(r'=+\r\n', dump)
        return dump

    @classmethod
    def loading_issues_from_dump(cls, dump: str) -> str:
        return cls._split_dump(dump)[2]

    @classmethod
    def chop_results(cls, dump: str) -> list[str]:
        import re
        dump = re.split(r'-{61,}', dump)
        return [block for block in dump if 'Vortex Lattice Output' in block]

    @classmethod
    def results_from_dump(cls, dump: str) -> list[dict[str, float]]:
        dump = cls._split_dump(dump)
        if len(dump) < 6: return []
        results = cls.chop_results(dump[4])
        stripped = []
        import re
        for result in results:
            result = re.split(r'Run case:.*\r\n', result, re.DOTALL)[1]
            result = re.split(r'-+\r\n', result)[0]
            stripped.append(str(result))
        values = []
        for result in stripped:
            vals = re.sub(r'\s+=\s+', '=', result)
            vals = re.sub(r'\r\n', '', vals)
            vals = vals.split()
            values.append({})
            for line in vals:
                if not '=' in line: continue
                key, value = line.split('=')
                values[-1][key] = float(value)

        return values

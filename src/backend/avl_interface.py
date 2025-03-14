from .geo_design import Geometry
from pathlib import Path


avl_path = Path(r"C:\Users\kazio\PycharmProjects\bipolAPI\src\avl\avl.exe")
local_path = Path(r"C:\Users\kazio\PycharmProjects\bipolAPI\src\temp_files_dir")


class AVLInterface:
    def __init__(self, geometry: Geometry) -> None:
        self.geometry = geometry

    @classmethod
    def execute_case(cls, geometry: Geometry, run_file_contents: str) -> str:
        avl_file = open(local_path.joinpath('local.avl'), 'w')
        run_file = open(local_path.joinpath('local.run'), 'w')
        avl_file.write(geometry.string())
        run_file.write(run_file_contents)
        avl_file.close()
        run_file.close()

        from subprocess import Popen, PIPE
        avl = Popen([avl_path, str(local_path.joinpath('local.avl'))], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        command = 'OPER\nX\n'
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
    def results_from_dump(cls, dump: str) -> list[dict[str, float]]:
        dump = cls._split_dump(dump)
        if len(dump) < 6: return []
        results = dump[4:-1]
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

from pathlib import Path
from ....backend.load_from_csv import load_from_csv


class FilesManager:
    def __init__(self):
        self.files_dicts: dict[str, dict[str, list[float]]] = {}

    def load_file(self, path: Path|str):
        path = Path(path)
        data = load_from_csv(path)
        if isinstance(data, list):
            data_dict = {f'Series {i+1}': line for i, line in enumerate(data)}
        else:
            data_dict = data
        self.files_dicts[path.name] = data_dict

    @property
    def file_names(self):
        return list(self.files_dicts.keys())

    def series_names(self, file_name):
        return list(self.files_dicts[file_name].keys())

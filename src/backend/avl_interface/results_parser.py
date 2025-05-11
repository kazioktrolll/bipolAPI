from pathlib import Path
import re

val_dict = dict[str, float]


class ResultsParser:
    @classmethod
    def _split_dump(cls, dump: str) -> list[str]:
        """Splits the dump string on === lines."""
        dump = re.split(r'=+\r\n', dump)
        return dump

    @classmethod
    def loading_issues_from_dump(cls, dump: str) -> str | None:
        """Returns the issue part of the dump."""
        issues = cls._split_dump(dump)[2]
        geom, mass, run = re.split(r'-{8,}', issues)
        if '*' in geom: return '\n'.join([line for line in geom.splitlines() if '*' in line])
        return None

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
        try:
            for path in paths:
                with open(path) as f: data = f.read()
                data = cls.st_file_to_dict(data)
                data = cls.split_st_dict(data)
                data[0] = cls.sort_forces_dict(data[0])
                data[1] = cls.sort_st_dict(data[1])
                _r.append(data)
            return _r
        except FileNotFoundError:
            return []

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
        try:
            ClbCnr = st_dict.pop('Clb_Cnr/Clr_Cnb')
        except KeyError:
            ClbCnr = 0
        dicts: dict[str, val_dict] = {}
        for k, v in st_dict.items():
            category = k[-2:] if k[-2] == 'd' else k[-1:]
            if category not in dicts: dicts[category] = {}
            dicts[category][k] = v

        dicts['misc'] = {'Xnp': Xnp, 'Clb_Cnr/Clr_Cnb': ClbCnr}
        if join: return {k: v for d in dicts.values() for k, v in d.items()}
        return dicts

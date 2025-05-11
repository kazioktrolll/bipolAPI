"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from pathlib import Path


def load_from_csv(path: Path | str) -> dict[str, list[float]] | list[list[float]]:
    if isinstance(path, str): path = Path(path)
    with open(path) as f:
        data = f.readlines()
    raw_vals = [line.split(',') for line in data]
    try:
        float(raw_vals[0][0])
        return to_columns(raw_vals)
    except ValueError:
        return to_dict(raw_vals)


def to_columns(raw_vals: list[list[str]]) -> list[list[float]]:
    float_rows = [[float(val) for val in line] for line in raw_vals]
    columns = []
    for i in range(len(raw_vals[0])): columns.append([.0] * len(raw_vals))
    for i in range(len(float_rows)):
        for j in range(len(float_rows[0])):
            columns[j][i] = float_rows[i][j]
    return columns


def to_dict(raw_vals: list[list[str]]) -> dict[str, list[float]]:
    keys = raw_vals.pop(0)
    cols = to_columns(raw_vals)
    return {k: c for k, c in zip(keys, cols)}

"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from functools import cached_property
from pathlib import Path
from .scene import Scene
from ..frontend import CalcDisplay


class CalcScene(Scene):
    @cached_property
    def display(self):
        return CalcDisplay(self, Path(self.app.work_dir.name))

    def build(self) -> None:
        self.app.geometry.distribute_points()
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.display.grid(row=0, column=0, sticky='news')

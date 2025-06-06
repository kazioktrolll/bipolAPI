"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkButton
from pathlib import Path
from src.backend import ImageGetter



class PlotButton(CTkButton):
    def __init__(self, parent, calc_display, app_wd: str | Path):
        super().__init__(parent, text='Plot Trefftz', command=self.plot)
        self._calc_display = calc_display
        self.app_wd = app_wd

    @property
    def calc_display(self):
        from .calc_display import CalcDisplay
        assert isinstance(self._calc_display, CalcDisplay)
        return self._calc_display

    @property
    def current_page(self):
        return self.calc_display.results_display.page

    def plot(self):
        geometry = self.calc_display.geometry
        run_file_data: dict[str, list[float]] = self.calc_display.oip.get_run_file_data()[0]
        case_number: int = self.current_page
        png_path = ImageGetter.get_trefftz(geometry, run_file_data, case_number, self.app_wd)
        #TODO: fix this so it displays the image on the path

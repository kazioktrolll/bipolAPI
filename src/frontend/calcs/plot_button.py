"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkButton
from pathlib import Path
from src.backend import PlotWindow



class PlotButton(CTkButton):
    def __init__(self, parent, calc_display, cwd: str | Path):
        from ...backend import PlotWindow
        super().__init__(parent, text='Plot Trefftz', command=self.toggle)
        self.plot_window: PlotWindow | None = None
        self._calc_display = calc_display
        self.cwd = cwd

    @property
    def calc_display(self):
        from .calc_display import CalcDisplay
        assert isinstance(self._calc_display, CalcDisplay)
        return self._calc_display

    @property
    def current_page(self):
        return self.calc_display.results_display.page

    def toggle(self):
        if self.plot_window is None:
            self.plot()
        else:
            self.close()

    def plot(self):
        geometry = self.calc_display.geometry
        run_file_data: dict[str, list[float]] = self.calc_display.oip.get_run_file_data()[0]
        case_number: int = self.current_page
        self.plot_window = PlotWindow.plot_trefftz(geometry, run_file_data, self.cwd, case_number)
        self.configure(text='Close')

    def close(self):
        self.plot_window.close()
        self.configure(text='Plot Trefftz')
        self.plot_window = None

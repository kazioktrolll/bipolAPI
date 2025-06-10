"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""
from pathlib import Path
from customtkinter import CTkFrame, CTkButton, CTkLabel
from threading import Thread
from .results_display import ResultsDisplay
from .oper_input import OperSeriesInputPanel
from .static_input import StaticInputPanel
from ..help_top_level import HelpTopLevel
from ..popup import Popup
from ..ask_popup import AskPopup


class CalcDisplay(CTkFrame):
    def __init__(self, parent, app_wd: str | Path):
        super().__init__(parent, fg_color='transparent')
        self.app_wd = Path(app_wd)

        self.left_frame = CTkFrame(self, fg_color='transparent', border_width=3)
        self.right_frame = CTkFrame(self, fg_color='transparent', border_width=3)
        self.left_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        self.right_frame.grid(row=0, column=2, sticky='nsew', padx=20, pady=20)

        self.exec_button = CTkButton(self.left_frame, text='Execute', command=self.run_case)

        controls_names = [c.name for c in self.geometry.get_controls()]
        self.results_display = ResultsDisplay(self.right_frame, self, controls_names, app_wd)
        self.oip = OperSeriesInputPanel(self.left_frame, controls_names)
        self.static_input = StaticInputPanel(self.left_frame, self.geometry.ref_pos.tuple())

        self.build()

    @property
    def geometry(self):
        from ...backend.geo_design import Geometry
        from ...scenes import Scene
        assert isinstance(self.master, Scene)
        assert isinstance(self.master.app.geometry, Geometry)
        return self.master.app.geometry

    def build(self):
        self.rowconfigure(0, weight=1)

        self.oip.grid(row=0, column=0, sticky="news", padx=20, pady=20)
        self.static_input.grid(row=1, column=0, sticky="news", padx=20, pady=20)
        self.left_frame.rowconfigure(2, weight=1)
        self.exec_button.grid(row=2, column=0, sticky='news', padx=20, pady=20)

        self.columnconfigure(1, weight=1)

        self.results_display.grid(row=0, column=1, sticky='news', padx=20, pady=20)

        self.run_case()

    def update(self):
        self.build()
        self.results_display.update()

    def get_data(self):
        try:
            oip_data, size = self.oip.get_run_file_data()
            return self.static_input.get_data(size) | oip_data
        except ValueError as e:
            HelpTopLevel(self, e.args[0])
            return None
        except ResourceWarning:
            force = AskPopup.ask('It is highly discouraged to run more than a thousand cases at once.\nContinue anyway?',
                                 ['Cancel', 'Continue'], 'Cancel')
            print(force)
            if force == 'Cancel': return None
            return self.oip.get_run_file_data(forced=True)

    def run_case(self):
        from ...backend import AVLInterface, AbortFlag

        self.exec_button.configure(state='disabled')
        popup = Popup(self)
        CTkLabel(popup, text='Running...').grid(row=0, column=0)
        abort_button = CTkButton(popup, text='Cancel')
        abort_button.grid(row=1, column=0)
        popup.run()
        data = self.get_data()
        abort_flag = AbortFlag()

        def task():
            vals, errors = AVLInterface.run_series(self.geometry, data, self.static_input.height, abort_flag, self.app_wd)
            self.after(0, on_task_done, *(vals, errors))

        def abort():
            abort_flag.abort()
            on_task_done()

        def on_task_done(vals=None, errors=''):
            popup.destroy()
            self.exec_button.configure(state='normal')
            if abort_flag: return
            if errors:
                self.run_errors(errors)
                return
            if vals:
                self.results_display.set_results(vals)

        if data:
            abort_button.configure(command=abort)
            self.update_idletasks()
            Thread(target=task).start()
        else:
            on_task_done()

    def run_errors(self, errors):
        for e in errors.split('\n') if errors else []:
            self.error(e)

    def error(self, text: str) -> None:
        HelpTopLevel(self, text)

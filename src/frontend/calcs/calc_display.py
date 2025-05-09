from customtkinter import CTkFrame, CTkButton
from .results_display import ResultsDisplay
from .oper_input import OperSeriesInputPanel
from ..help_top_level import HelpTopLevel


class CalcDisplay(CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color='transparent')
        self.left_frame = CTkFrame(self, fg_color='transparent', border_width=3)
        self.right_frame = CTkFrame(self, fg_color='transparent', border_width=3)
        self.left_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        self.right_frame.grid(row=0, column=2, sticky='nsew', padx=20, pady=20)

        self.exec_button = CTkButton(self.left_frame, text='Execute', command=self.run_case)

        controls_names = [c.class_name for c in self.geometry.get_controls()]
        self.results_display = ResultsDisplay(self.right_frame, self, controls_names)
        self.oip = OperSeriesInputPanel(self.left_frame, controls_names)

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

        self.oip.grid(row=0, column=0, sticky="nw", padx=20, pady=20)
        self.left_frame.rowconfigure(1, weight=1)
        self.exec_button.grid(row=1, column=0, sticky='news', padx=20, pady=20)

        self.columnconfigure(1, weight=1)

        self.results_display.grid(row=0, column=1, sticky='news', padx=20, pady=20)

        self.run_case()

    def update(self):
        self.build()
        self.results_display.update()

    def run_case(self):
        from ...backend import AVLInterface

        self.exec_button.configure(state='disabled')
        data = self.oip.get_run_file_data()
        vals, errors = AVLInterface.run_series(self.geometry, data)
        if errors:
            self.run_errors(errors)
            return
        self.results_display.set_results(vals)
        self.exec_button.configure(state='normal')

    def run_errors(self, errors):
        for e in errors.split('\n') if errors else []:
            self.error(e)

    def error(self, text: str) -> None:
        HelpTopLevel(self, text)

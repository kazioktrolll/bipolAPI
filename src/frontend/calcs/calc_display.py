from customtkinter import CTkFrame
from .results_display import ResultsDisplay


class CalcDisplay(CTkFrame):
    def __init__(self, parent):
        from .oper_input import OperSeriesInputPanel
        super().__init__(parent)
        self.ois_frame = None
        self.exec_button = None
        self.results_display: ResultsDisplay | None = None
        self.oip: OperSeriesInputPanel | None = None
        self.build()

    @property
    def geometry(self):
        from ...backend.geo_design import Geometry
        from ...scenes import Scene
        assert isinstance(self.master, Scene)
        assert isinstance(self.master.app.geometry, Geometry)
        return self.master.app.geometry

    def build(self):
        from .oper_input import OperSeriesInputPanel
        controls = self.geometry.get_controls()
        controls_names = [c.name for c in controls]
        self.oip = OperSeriesInputPanel(self, controls_names)
        self.oip.grid(row=0, column=0, sticky="nsew")

        from customtkinter import CTkButton
        self.exec_button = CTkButton(self, text='Execute', command=self.run_case)
        self.rowconfigure(2, weight=1)
        self.exec_button.grid(row=1, column=0, sticky='news')
        self.results_display = ResultsDisplay(self)
        self.columnconfigure(1, minsize=10)
        self.results_display.grid(row=0, column=2, rowspan=2, sticky='news')
        self.run_case()

    def update(self):
        self.build()
        self.results_display.update()

    def run_case(self):
        from ...backend import AVLInterface

        self.exec_button.configure(state='disabled')
        data = self.oip.get_run_file_data()
        vals = AVLInterface.run_series(self.geometry, data)
        self.results_display.set_results(vals)
        self.exec_button.configure(state='normal')

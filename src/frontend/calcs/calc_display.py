from customtkinter import CTkFrame


class CalcDisplay(CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.ois_frame = None
        self.exec_button = None
        self.results_label = None
        self.oip = None

    @property
    def geometry(self):
        from ...backend.geo_design import Geometry
        from ...scenes import Scene
        assert isinstance(self.master, Scene)
        assert isinstance(self.master.app.geometry, Geometry)
        return self.master.app.geometry

    def build(self):
        from ...frontend import OperInputPanel
        self.oip = OperInputPanel(self, ['flap', 'aileron', 'elevator'])
        self.oip.grid(row=0, column=0, sticky="nsew")

        from customtkinter import CTkButton, CTkLabel
        self.exec_button = CTkButton(self, text='Execute', command=self.run_case)
        self.exec_button.grid(row=1, column=0, sticky='news')
        self.results_label = CTkLabel(self)
        self.columnconfigure(1, minsize=10)
        self.results_label.grid(row=0, column=2, sticky='news')
        self.run_case()

    def run_case(self):
        from ...backend import AVLInterface

        self.exec_button.configure(state='disabled')
        dump = AVLInterface.execute_case(
            self.geometry,
            f"Run case  1: AutoCase\nX_cg = {self.geometry.ref_pos.x}\n" + self.oip.run_file_string()
        )
        vals = AVLInterface.results_from_dump(dump)[0]
        results_string = '\n'.join([': '.join([k, str(v)]) for k, v in vals.items()])
        self.results_label.configure(text=results_string)
        self.exec_button.configure(state='normal')

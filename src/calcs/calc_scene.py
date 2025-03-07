from ..scenes import Scene
from .frontend import OperInputPanel
from customtkinter import CTkFrame


class CalcScene(Scene):
    def __init__(self, parent, app):
        self.ois_frame = None
        self.exec_button = None
        self.results_label = None
        self._app = app
        self.oip = None
        super().__init__(parent)

    @property
    def app_test(self):
        from .app import App
        assert isinstance(self._app, App)
        return self._app

    def build(self) -> None:
        self.oip = OperInputPanel(self, ['Ailerons'])
        self.oip.grid(row=0, column=0, sticky="nsew")

        from customtkinter import CTkButton, CTkLabel
        self.exec_button = CTkButton(self, text='Execute', command=self.run_case)
        self.exec_button.grid(row=1, column=0, sticky='news')
        self.results_label = CTkLabel(self)
        self.columnconfigure(1, minsize=10)
        self.results_label.grid(row=0, column=2, sticky='news')
        self.run_case()

    def run_case(self):
        from .avl_communicator import Interface

        self.exec_button.configure(state='disabled')
        dump = Interface.execute_case(
            self.app_test.geometry,
            f"Run case  1: AutoCase\nX_cg = {self.app_test.geometry.ref_pos.x}\n" + self.oip.run_file_string()
        )
        vals = Interface.results_from_dump(dump)[0]
        results_string = '\n'.join([': '.join([k, str(v)]) for k, v in vals.items()])
        self.results_label.configure(text=results_string)
        self.exec_button.configure(state='normal')

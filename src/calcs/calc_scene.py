from ..scenes import Scene
from ..frontend import ParameterField
from customtkinter import CTkFrame


class CalcScene(Scene):
    def __init__(self, parent, app):
        self.pfs_frame = None
        self.exec_button = None
        self.results_label = None
        self._app = app
        self.pfs: dict[str, ParameterField] = {}
        super().__init__(parent)

    @property
    def app_test(self):
        from .app import App
        assert isinstance(self._app, App)
        return self._app

    def build(self) -> None:
        self.pfs_frame = CTkFrame(self)
        self.pfs_frame.grid(row=0, column=0, sticky="nsew")
        # a b r p y c+
        pfs_data = (
            ('alfa', 'Alfa', '', lambda a: True, 0),
            ('beta', 'Beta', '', lambda b: True, 0),
            ('roll', 'Roll', '', lambda r: True, 0),
            ('pitch', 'Pitch', '', lambda p: True, 0),
            ('yaw', 'Yaw', '', lambda y: True, 0),
        )
        for i, pf_data in enumerate(pfs_data):
            pf = ParameterField(self.pfs_frame, name=pf_data[1], help_message=pf_data[2], assert_test=pf_data[3])
            pf.set(pf_data[4])
            pf.grid(row=i, column=0, sticky='news')
            self.pfs[pf_data[0]] = pf

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
            alfa=self.pfs['alfa'].value,
            beta=self.pfs['beta'].value,
            roll_rate=self.pfs['roll'].value,
            pitch_rate=self.pfs['pitch'].value,
            yaw_rate=self.pfs['yaw'].value,
        )
        vals = Interface.results_from_dump(dump)[0]
        results_string = '\n'.join([': '.join([k, str(v)]) for k, v in vals.items()])
        self.results_label.configure(text=results_string)
        self.exec_button.configure(state='normal')

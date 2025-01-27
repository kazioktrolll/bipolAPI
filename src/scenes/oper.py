from .scene import Scene, App
from ..frontend import ParameterField
from customtkinter import CTkButton, CTkFrame
from ..demo import *


class OperScene(Scene):
    def __init__(self, app:App, param_names:list[str]):
        self.param_names = param_names
        self.inputs: dict[str, ParameterField] = {}
        super().__init__(app)

    def build(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left_frame = CTkFrame(self)
        left_frame.grid(column=0, row=0, sticky='nsew')
        left_frame.columnconfigure(0, weight=1)

        for i, name in enumerate(self.param_names):
            field = ParameterField(left_frame, name)
            self.inputs[name] = field
            field.grid(column=0, row=i, sticky='nsew')

        self.fake_output = FakeOutput(self)
        self.fake_output.grid(column=1, row=0, sticky='nsew')

        CTkButton(left_frame, text="Run",
                  command=lambda: 1/0
                  ).grid(column=0, row=6, sticky='nsew')
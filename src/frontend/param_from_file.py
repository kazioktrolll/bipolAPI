from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkEntry
from pathlib import Path
from .popup import Popup


class ParamFromFile(CTkFrame):
    path: Path | None
    def __init__(self, parent):
        super().__init__(parent)
        self.path = None

        self.name_label = CTkLabel(self, text="", width=100)
        self.name_label.grid(row=0, column=0, sticky="nsw", padx=5, pady=5)

        self.columnconfigure(1, weight=1)

        CTkButton(self, text="Load from File"
                  ).grid(row=0, column=2, sticky="nse", padx=5, pady=5)
        CTkButton(self, text="Symmetric NACA", command=self.load_naca
                  ).grid(row=2, column=2, sticky="nse", padx=5, pady=5)

    def load_naca(self):
        window = Popup(self, "Load NACA")
        entry = CTkEntry(window)
        entry.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        CTkButton(window, text="Set", width=50
                  ).grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        window.run()

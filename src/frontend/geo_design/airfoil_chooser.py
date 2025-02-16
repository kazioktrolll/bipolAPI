from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkEntry
from tkinter import filedialog
from pathlib import Path

from ..popup import Popup
from ..help_top_level import HelpTopLevel
from ...backend.geo_design import Airfoil


class AirfoilChooser(CTkFrame):
    path: Path | None
    def __init__(self, parent):
        super().__init__(parent)
        self.path = None

        self.airfoil = Airfoil.empty()

        self.file_label = CTkLabel(self, text="", width=100)
        self.file_label.grid(row=0, column=0, sticky="nsw", padx=5, pady=5)

        self.naca_label = CTkLabel(self, text="", width=100)
        self.naca_label.grid(row=2, column=0, sticky="nsw", padx=5, pady=5)

        self.columnconfigure(1, weight=1)

        CTkButton(self, text="Load from File", command=self.load_from_file
                  ).grid(row=0, column=2, sticky="nse", padx=5, pady=5)
        CTkButton(self, text="Symmetric NACA", command=self.load_naca
                  ).grid(row=2, column=2, sticky="nse", padx=5, pady=5)

    def load_naca(self):
        window = Popup(self, "Load NACA")
        entry = CTkEntry(window)
        entry.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        def get_airfoil():
            try: self.airfoil = Airfoil.from_naca(entry.get())
            except ValueError:
                HelpTopLevel(self, "Incorrect NACA code!")
                entry.delete(0, "end")
                return

            self.naca_label.configure(text=f"NACA {self.airfoil.name}")
            self.file_label.configure(text="")
            window.destroy()

        CTkButton(window, text="Set", width=50, command=get_airfoil
                  ).grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        window.run()

    def load_from_file(self):
        path = Path(filedialog.askopenfilename(title="Select File",
                                               filetypes=(("DAT, CSV, TXT Files", ".dat .csv .txt"),
                                                          ("All Files", ".*"))))
        try: self.airfoil = Airfoil.from_file(name=path.name, path=path)
        except ValueError:
            HelpTopLevel(self, "Incorrect input file!")
            return
        self.file_label.configure(text=self.airfoil.name)
        self.naca_label.configure(text="")
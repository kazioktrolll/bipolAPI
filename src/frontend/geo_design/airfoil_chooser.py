"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkButton, CTkLabel
from tkinter import filedialog
from pathlib import Path

from ..advanced_entry import AdvancedEntry
from ..popup import Popup
from ..help_top_level import HelpTopLevel
from ...backend.geo_design import Airfoil
from ...backend import handle_crash


class AirfoilChooser(CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, border_width=3)
        self.path: Path | None = None
        self.airfoil = Airfoil.empty()

        self.name_label = CTkLabel(self, text="Choose Airfoil:", width=100)
        self.name_label.grid(row=0, column=0, sticky="nsw", padx=5, pady=5)

        self.airfoil_label = CTkLabel(self, text="", width=100)
        self.airfoil_label.grid(row=2, column=0, sticky="nsw", padx=5, pady=5)

        self.columnconfigure(1, weight=1)

        CTkButton(self, text="Load from File", command=self.load_from_file
                  ).grid(row=0, column=2, sticky="nse", padx=8, pady=8)
        CTkButton(self, text="NACA", command=self.load_naca
                  ).grid(row=2, column=2, sticky="nse", padx=8, pady=8)

    @handle_crash
    def load_naca(self):
        window = Popup(self)
        entry = AdvancedEntry(window.frame)
        entry.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        @handle_crash
        def get_airfoil():
            try:
                self.airfoil = Airfoil.from_naca(entry.get())
            except ValueError:
                HelpTopLevel(self, "Incorrect NACA code!")
                entry.delete(0, "end")
                return

            self.airfoil_label.configure(text=f"NACA {self.airfoil.name}")
            window.destroy()

        CTkButton(window.frame, text="Set", width=50, command=get_airfoil
                  ).grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        window.run()

    @handle_crash
    def load_from_file(self):
        path = Path(filedialog.askopenfilename(title="Select File",
                                               filetypes=(("DAT, CSV, TXT Files", ".dat .csv .txt"),
                                                          ("All Files", ".*"))))
        try:
            self.airfoil = Airfoil.from_file(name=path.name, path=path)
        except ValueError:
            HelpTopLevel(self, "Incorrect input file!")
            return
        self.airfoil_label.configure(text=self.airfoil.name)

    def set(self, airfoil: Airfoil):
        self.airfoil = airfoil
        self.airfoil_label.configure(text=f"NACA {airfoil.name}")

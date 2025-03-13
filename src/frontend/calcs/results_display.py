from customtkinter import CTkFrame, CTkSegmentedButton, CTkLabel, CTkEntry


class ResultsDisplay(CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=parent.cget('fg_color'))
        self.results: list[dict[str, float]] = [{}]
        self.page = 0
        self.page_button = CTkSegmentedButton(self, command=self.switch_page)
        self.mode_button = CTkSegmentedButton(self, values=['Simple', 'Full'], command=self.switch_mode)
        self.simple_label = TextBox(self)
        self.full_label = TextBox(self)
        self.current_label = self.simple_label
        self.mode_button.set('Simple')
        self.build()

    @property
    def active_results(self):
        return self.results[self.page]

    def build(self):
        self.set_results([{}])

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=0)

        self.page_button.grid(row=0, column=0, sticky='nsew')
        self.mode_button.grid(row=1, column=0, sticky='nsew')
        self.current_label.grid(row=2, column=0, sticky='nsew')
        self.update()

    def update(self):
        simple_keys = [
            'Alpha',
            'pb/2V',
            'Beta',
            'qc/2V',
            'rb/2V',
            'Cltot',
            'CYtot',
            'Cmtot',
            'Cntot',
            'CLtot',
            'CDtot',
            'CDind'
        ] + [c.name for c in self.control_surfaces()]
        simple_results = {k:v for k, v in self.active_results.items() if k in simple_keys}
        self.simple_label.set_data(simple_results)
        self.full_label.set_data(self.active_results)

        self.simple_label.place(x=1e4, y=8576)
        self.full_label.place(x=1e4, y=5592)
        self.current_label.grid(row=2, column=0, sticky='nsew')



    def switch_mode(self, mode: str):
        match mode:
            case 'Simple': self.current_label = self.simple_label
            case 'Full': self.current_label = self.full_label
        self.update()

    def set_results(self, results: list[dict[str, float]]):
        self.results = results
        pages = list(range(len(results)))
        self.page_button.configure(values=list(map(str, pages)))
        self.page_button.set('0')
        self.update()

    def switch_page(self, page: str):
        self.page = int(page)
        self.update()

    def control_surfaces(self):
        from .calc_display import CalcDisplay
        assert isinstance(self.master, CalcDisplay)
        return self.master.geometry.get_controls()


class TextBox(CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=parent.cget('fg_color'))
        self.dict = {}
        self.build()

    def build(self):
        for i, (key, value) in enumerate(self.dict.items()):
            CTkLabel(self, text=key, anchor="w").grid(row=i, column=0, padx=5, sticky="w")

            entry = CTkEntry(self, width=100, border_width=0, fg_color='transparent')
            entry.insert(0, str(value))
            entry.configure(state="readonly")  # Make text selectable but not editable
            entry.grid(row=i, column=1, padx=5, sticky="w")

    def set_data(self, data: dict[str, float]):
        self.dict = data
        self.build()

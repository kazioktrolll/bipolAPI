from customtkinter import CTkFrame, CTkSegmentedButton, CTkLabel, CTkEntry, CTkButton


class ResultsDisplay(CTkFrame):
    def __init__(self, parent, controls_names: list[str]):
        super().__init__(parent, fg_color=parent.cget('fg_color'))
        self.controls_names = controls_names
        self.results: list[list[dict[str, float]]] = [[{}, {}]]
        self.page = 0
        self.page_button = CTkSegmentedButton(self, command=self.switch_page)
        self.mode_button = CTkSegmentedButton(self, values=['Simple', 'Stability', 'Full'], command=self.switch_mode)
        self.csv_button = CTkButton(self, text='Save to .csv', command=self.save_to_csv)
        self.simple_label = TextBox(self)
        self.stability_label = STDisplay(self, controls_names)
        self.full_label = TextBox(self)
        self.current_label = self.simple_label
        self.mode_button.set('Simple')
        self.build()

    @property
    def active_results(self):
        return self.results[self.page]

    def build(self):
        self.set_results([[{}, {}]])

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        self.page_button.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.mode_button.grid(row=1, column=0, sticky='nsew')
        self.csv_button.grid(row=1, column=1, sticky='nsew')
        self.current_label.grid(row=2, column=0, columnspan=2, sticky='nsew')
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
        ] + self.controls_names
        simple_results = {k:v for k, v in self.active_results[0].items() if k in simple_keys}
        self.simple_label.set(simple_results)
        self.stability_label.set(self.active_results[1])
        self.full_label.set(self.active_results[0])

        self.simple_label.place(x=1e4, y=8576)
        self.stability_label.place(x=1e4, y=9366)
        self.full_label.place(x=1e4, y=5592)
        self.current_label.grid(row=2, column=0, columnspan=2, sticky='nsew')

    def switch_mode(self, mode: str):
        match mode:
            case 'Simple': self.current_label = self.simple_label
            case 'Stability': self.current_label = self.stability_label
            case 'Full': self.current_label = self.full_label
        self.update()

    def set_results(self, results: list[list[dict[str, float]]]):
        self.results = results
        pages = list(range(len(results)))
        self.page_button.configure(values=list(map(str, pages)))
        self.page_button.set('0')
        self.update()

    def switch_page(self, page: str):
        self.page = int(page)
        self.update()

    def save_to_csv(self):
        from pathlib import Path
        from tkinter.filedialog import asksaveasfilename
        path = Path(asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV File', ['*.csv']), ('All files', ['*.*'])],
            title='Gavl_results',
            confirmoverwrite=True
        ))
        to_save = ''
        for key in (self.active_results[0] | self.active_results[1]).keys():
            to_save += f'{key},'
        to_save = to_save[:-1]
        to_save += '\n'
        for i in range(len(self.results)):
            for val in (self.results[i][0] | self.results[i][1]).values():
                to_save += f'{val},'
            to_save = to_save[:-1]
            to_save += '\n'
        to_save = to_save[:-1]
        with open(path, 'w') as f: f.write(to_save)


class TextBox(CTkFrame):
    def __init__(self, parent, name:str=None):
        super().__init__(parent, fg_color='transparent', border_color='gray30', border_width=2)
        self.is_named = name is not None
        self.name_label = CTkLabel(self, text=name or '', anchor='w')
        self.dict = {}
        self.build()

    def build(self):
        if self.is_named: self.name_label.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        for i, (key, value) in enumerate(self.dict.items()):
            CTkLabel(self, text=key, anchor="e").grid(row=i+1, column=0, padx=5, pady=2, sticky="e")

            entry = CTkEntry(self, width=100, border_width=0, fg_color='transparent')
            entry.insert(0, str(value))
            entry.configure(state="readonly")  # Make text selectable but not editable
            entry.grid(row=i+1, column=1, padx=5, pady=2, sticky="w")

    def set(self, data: dict[str, float]):
        self.dict = data
        self.build()


class STDisplay(CTkFrame):
    def __init__(self, parent, controls_names: list[str]):
        super().__init__(parent, fg_color='transparent')
        self.controls = list(dict.fromkeys(controls_names)) # Remove duplicates
        self.dict: dict[str, float] = {}

    def get_split_dict(self) -> list[dict[str, float]]:
        blocks: list[dict[str, float]] = []
        for k, v in self.dict.items():
            if 'CL' in k: blocks.append({})
            blocks[-1][k] = v
        Xnp = blocks[-1].pop('Xnp')
        Clb = blocks[-1].pop('Clb_Cnr/Clr_Cnb')
        blocks.append({'Xnp': Xnp, 'ClbCnr/ClrCnb': Clb})
        return blocks

    def display_blocks(self, blocks: list[dict[str, float]]):
        assert len(blocks) >= 5 # There should be 5 basic (alfa, beta, roll, pitch, yaw) and potentially more from control surfaces
        # Grid the basic ones
        for name, pos in {'Alpha':(0,0), 'Beta':(0,1), 'Roll Rate':(1, 0), 'Pitch Rate':(1, 1), 'Yaw Rate':(1,2)}.items():
            tb = TextBox(self, name)
            tb.columnconfigure(0, minsize=70)
            tb.set(blocks.pop(0))
            r, c = pos
            tb.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
        # Now grid the additional ones in rows 3 wide
        if not blocks: return
        for i, block in enumerate(blocks):
            try: name = self.controls[i].capitalize() + 's'
            except IndexError: name = None
            tb = TextBox(self, name)
            tb.columnconfigure(0, minsize=70)
            tb.set(block)
            r = 2 + i//3
            c = i%3
            tb.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

    def set(self, data: dict[str, float]) -> None:
        self.dict = data
        children = list(self.children.values())
        for i in range(len(children)+1, -1, 1): children[i-1].destroy()
        if not data: return
        self.display_blocks(self.get_split_dict())

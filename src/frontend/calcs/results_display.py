"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkSegmentedButton, CTkLabel, CTkEntry, CTkButton
from pathlib import Path
from .plot_button import PlotTrefftz


class ResultsDisplay(CTkFrame):
    def __init__(self, parent, calc_display, controls_names: list[str], app_wd: str | Path):
        super().__init__(parent, fg_color=parent.cget('fg_color'))
        self.controls_names = controls_names
        self.results: list[list[dict[str, float]]] = [[{}, {}]]
        self.page = 0
        self.page_button = PagesNumberStrip(self, command=self.switch_page)
        self.mode_button = CTkSegmentedButton(self, values=['Forces', 'Stability'], command=self.switch_mode)
        self.csv_button = CTkButton(self, text='Save to .csv', command=self.save_to_csv)
        self.forces_display = ForcesDisplay(self, controls_names)
        self.stability_display = STDisplay(self, controls_names)
        self.current_display = self.forces_display
        self.plot_button = PlotTrefftz(self, app_wd, calc_display)
        self.mode_button.set('Forces')
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

        self.rowconfigure(0, minsize=30)
        self.page_button.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.page_button.hide()
        self.mode_button.grid(row=1, column=0, sticky='nsew', padx=3, pady=6)
        self.csv_button.grid(row=1, column=1, sticky='nsew', padx=3, pady=6)
        self.current_display.grid(row=2, column=0, columnspan=2, sticky='nsew')
        self.plot_button.grid(row=3, column=0, columnspan=2, sticky='nsew', pady=10, padx=5)
        self.update()

    def update(self):
        self.forces_display.set(self.active_results[0])
        self.stability_display.set(self.active_results[1])

        self.stability_display.place(x=1e4, y=9366)
        self.forces_display.place(x=1e4, y=5592)
        self.current_display.grid(row=2, column=0, columnspan=2, sticky='nsew')

    def switch_mode(self, mode: str):
        match mode:
            case 'Forces':
                self.current_display = self.forces_display
            case 'Stability':
                self.current_display = self.stability_display
        self.update()

    def set_results(self, results: list[list[dict[str, float]]]):
        self.results = results
        self.page_button.set_size(len(results))
        self.update()

    def switch_page(self, page: str):
        self.page = int(page) - 1
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
        with open(path, 'w') as f:
            f.write(to_save)


class TextBox(CTkFrame):
    def __init__(self, parent, name: str = None):
        super().__init__(parent, fg_color='transparent', border_color='gray30', border_width=2)
        self.is_named = name is not None
        self.name_label = CTkLabel(self, text=name or '', anchor='w')
        self.dict = {}
        self.build()

    def build(self):
        self.columnconfigure(0, weight=0, minsize=5)
        if self.is_named: self.name_label.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        for i, (key, value) in enumerate(self.dict.items()):
            CTkLabel(self, text=key, anchor="e").grid(row=i + 1, column=1, padx=5, pady=2, sticky="e")

            entry = CTkEntry(self, width=100, border_width=0, fg_color='transparent')
            entry.insert(0, self._format(value))
            entry.configure(state="readonly")  # Make text selectable but not editable
            entry.grid(row=i + 1, column=2, padx=5, pady=2, sticky="w")

    def set(self, data: dict[str, float]):
        self.dict = data
        self.build()

    @staticmethod
    def _format(val: float) -> str:
        f = f'{val:.4f}'
        e = f'{val:.2e}'
        g = f'{val:.4g}'
        if val == 0.0:
            return g
        if abs(val) < 1.0e-02 and e[-2:] != '02':
            return e
        if abs(val) > 10:
            return g
        return f


class STDisplay(CTkFrame):
    def __init__(self, parent, controls_names: list[str]):
        super().__init__(parent, fg_color='transparent')
        self.controls = list(dict.fromkeys(controls_names))  # Remove duplicates
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
        assert len(blocks) >= 5  # There should be 5 basic (alfa, beta, roll, pitch, yaw) and potentially more from control surfaces
        # Grid the basic ones
        for name, pos in {'Alpha': (0, 0), 'Beta': (0, 1), 'Roll Rate': (1, 0), 'Pitch Rate': (1, 1), 'Yaw Rate': (1, 2)}.items():
            tb = TextBox(self, name)
            tb.columnconfigure(0, minsize=70)
            tb.set(blocks.pop(0))
            r, c = pos
            tb.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
        # Now grid the additional ones in rows 3 wide
        if not blocks: return
        for i, block in enumerate(blocks):
            try:
                name = self.controls[i].capitalize()
            except IndexError:
                name = None
            tb = TextBox(self, name)
            tb.columnconfigure(0, minsize=70)
            tb.set(block)
            r = 2 + i // 3
            c = i % 3
            tb.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

    def set(self, data: dict[str, float]) -> None:
        self.dict = data
        children = list(self.children.values())
        for i in range(len(children) + 1, -1, 1): children[i - 1].destroy()
        if not data: return
        self.display_blocks(self.get_split_dict())


class ForcesDisplay(CTkFrame):
    def __init__(self, parent, controls_names: list[str]):
        super().__init__(parent, fg_color='transparent')
        self.controls = list(dict.fromkeys(controls_names))  # Remove duplicates
        self.dict: dict[str, float] = {}

    def get_split_dict(self) -> list[dict[str, float]]:
        blocks: list[dict[str, float]] = []
        current_block: dict[str, float] | None = None
        breakpoints = [
            'Alpha',
            'pb/2V',
            "p'b/2V",
            'CXtot',
            'Cltot',
            "Cl'tot",
            'CLtot',
            'CDind'
        ]
        if self.controls: breakpoints.append(self.controls[0])

        for k, v in self.dict.items():
            if k in breakpoints:
                if current_block: blocks.append(current_block)
                current_block = {k: v}
            else:
                current_block[k] = v
        if current_block: blocks.append(current_block)

        return blocks

    def display_blocks(self, blocks: list[dict[str, float]]):
        for i, block in enumerate(blocks):
            tb = TextBox(self)
            tb.set(block)
            r = i // 3
            c = i % 3
            tb.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

    def set(self, data: dict[str, float]) -> None:
        self.dict = data
        children = list(self.children.values())
        for i in range(len(children) + 1, -1, 1): children[i - 1].destroy()
        if not data: return
        self.display_blocks(self.get_split_dict())


class PagesNumberStrip(CTkSegmentedButton):
    _size = 1
    _chapter_size = 20
    _current_chapter = 0
    _grid_data = {}

    @property
    def current_pages(self):
        try:
            return list(super()._buttons_dict.keys())
        except AttributeError:
            return []

    def set_size(self, size: int):
        if size == 1 and self.grid_info():
            self.hide()
        elif size > 1 and not self.grid_info():
            self.show()
        self._size = size
        self.goto(1)

    def goto(self, page: int):
        if str(page) not in self.current_pages:
            self.change_chapter(page)
        self.set(str(page))

    def change_chapter(self, page: int):
        do_previous = True
        do_next = True
        chapter = page // self._chapter_size
        self._current_chapter = chapter
        if chapter == 0: do_previous = False
        start = chapter * self._chapter_size + 1
        end = start + self._chapter_size - 1
        if end >= self._size:
            end = self._size
            do_next = False

        values = ['<'] if do_previous else []
        values += list(map(str, range(start, end + 1)))
        if do_next: values += ['>']

        self.configure(values=values)

    def previous(self):
        start_previous = (self._current_chapter - 1) * self._chapter_size
        self.change_chapter(start_previous)

    def next(self):
        start_previous = (self._current_chapter + 1) * self._chapter_size
        self.change_chapter(start_previous)

    def set(self, value: str, from_variable_callback: bool = False, from_button_callback: bool = False):
        if value == '<':
            self.previous()
        elif value == '>':
            self.next()
        else:
            super().set(value, from_variable_callback, from_button_callback)

    def grid(self, **kwargs):
        self._grid_data = kwargs
        super().grid(**kwargs)

    def hide(self):
        self.grid_forget()

    def show(self):
        self.grid(**self._grid_data)

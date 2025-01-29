from customtkinter import CTkCanvas, CTkFrame
from ..backend.geo_design import Section, Surface


class GeometryDisplay(CTkFrame):
    def __init__(self, parent, origin: tuple[int, int]):
        super().__init__(parent)
        self.canvas = CTkCanvas(self)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.origin = origin
        self.after(0, self.build)

    def build(self):
        self.display_CG(*self.origin)

    def display_CG(self, x, y):
        self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='yellow')

    def display_section(self, section: Section | list[Section]):
        if isinstance(section, list):
            for s in section:
                self.display_section(s)
            return

        assert isinstance(section, Section)

        xle = section.leading_edge_position[0]
        yle = section.leading_edge_position[1]
        xte  = section.trailing_edge_position[0]
        self.canvas.create_line(self.origin[0] + yle * 100, self.origin[1] + xle * 100,
                                self.origin[0] + yle * 100, self.origin[1] + xte * 100,
                                fill='blue', width=3, capstyle='round')

    def display_wing(self, wing: Surface):
        if len(wing.sections) < 2: raise Exception("Can't display a wing with less that 2 sections!")

        self.display_section(wing.sections[0])
        for i in range(1, len(wing.sections)):
            curr_sec = wing.sections[i]
            prev_sec = wing.sections[i-1]
            self.display_section(curr_sec)
            self.canvas.create_line(self.origin[0] + prev_sec.leading_edge_position[1] * 100,
                                    self.origin[1] + prev_sec.leading_edge_position[0] * 100,
                                    self.origin[0] + curr_sec.leading_edge_position[1] * 100,
                                    self.origin[1] + curr_sec.leading_edge_position[0] * 100,
                                    width=3, fill='gray70', capstyle='round')
            self.canvas.create_line(self.origin[0] + prev_sec.trailing_edge_position[1] * 100,
                                    self.origin[1] + prev_sec.trailing_edge_position[0] * 100,
                                    self.origin[0] + curr_sec.trailing_edge_position[1] * 100,
                                    self.origin[1] + curr_sec.trailing_edge_position[0] * 100,
                                    width=3, fill='gray70', capstyle='round')
            self.canvas.create_line(self.origin[0] + prev_sec.leading_edge_position[1] * 100,
                                    self.origin[1] + (prev_sec.leading_edge_position[0] + prev_sec.chord * .25) * 100,
                                    self.origin[0] + curr_sec.leading_edge_position[1] * 100,
                                    self.origin[1] + (curr_sec.leading_edge_position[0] + curr_sec.chord * .25) * 100,
                                    width=2, fill='red', capstyle='round', dash=20)
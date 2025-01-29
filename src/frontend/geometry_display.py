from customtkinter import CTkCanvas, CTkFrame
from ..backend.geo_design import Section, Surface, Geometry


class GeometryDisplay(CTkFrame):
    def __init__(self, parent, geometry: Geometry):
        super().__init__(parent)
        self.geometry = geometry
        self.canvas = CTkCanvas(self)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.scale = 100
        self.origin = (0, 0)

    def draw(self):
        for surface in self.geometry.surfaces.values():
            self.display_wing(surface)
        self.display_CG(*self.geometry.ref_pos[:2])

    def update(self):
        self.clear()
        self.origin = (self.winfo_width() / 2, self.winfo_height() / 2)
        self.draw()

    def display_CG(self, x, y):
        x *= self.scale
        y *= self.scale
        x += self.origin[1]
        y += self.origin[0]
        self.canvas.create_oval(y-5, x-5, y+5, x+5, fill='yellow')

    def display_section(self, section: Section | list[Section]):
        if isinstance(section, list):
            for s in section:
                self.display_section(s)
            return

        assert isinstance(section, Section)

        xle = section.leading_edge_position[0]
        yle = section.leading_edge_position[1]
        xte  = section.trailing_edge_position[0]
        self.canvas.create_line(self.origin[0] + yle * self.scale, self.origin[1] + xle * self.scale,
                                self.origin[0] + yle * self.scale, self.origin[1] + xte * self.scale,
                                fill='blue', width=3, capstyle='round')

    def display_wing(self, wing: Surface | list[Surface]):
        if isinstance(wing, list):
            for w in wing: self.display_wing(w)
            return
        assert isinstance(wing, Surface)

        if wing.y_duplicate:
            # If wing is symmetric, create a mirror copy of the wing,
            # display it, and the n continue displaying the original wing.
            ydup = wing.get_symmetric()
            ydup.y_duplicate = False
            self.display_wing(ydup)

        if len(wing.sections) < 2: raise Exception("Can't display a wing with less that 2 sections!")

        self.display_section(wing.sections[0])
        for i in range(1, len(wing.sections)):
            curr_sec = wing.sections[i]
            prev_sec = wing.sections[i-1]
            self.display_section(curr_sec)
            self.canvas.create_line(self.origin[0] + prev_sec.leading_edge_position[1] * self.scale,
                                    self.origin[1] + prev_sec.leading_edge_position[0] * self.scale,
                                    self.origin[0] + curr_sec.leading_edge_position[1] * self.scale,
                                    self.origin[1] + curr_sec.leading_edge_position[0] * self.scale,
                                    width=3, fill='gray70', capstyle='round')
            self.canvas.create_line(self.origin[0] + prev_sec.trailing_edge_position[1] * self.scale,
                                    self.origin[1] + prev_sec.trailing_edge_position[0] * self.scale,
                                    self.origin[0] + curr_sec.trailing_edge_position[1] * self.scale,
                                    self.origin[1] + curr_sec.trailing_edge_position[0] * self.scale,
                                    width=3, fill='gray70', capstyle='round')
            self.canvas.create_line(self.origin[0] + prev_sec.leading_edge_position[1] * self.scale,
                                    self.origin[1] + (prev_sec.leading_edge_position[0] + prev_sec.chord * .25) * self.scale,
                                    self.origin[0] + curr_sec.leading_edge_position[1] * self.scale,
                                    self.origin[1] + (curr_sec.leading_edge_position[0] + curr_sec.chord * .25) * self.scale,
                                    width=2, fill='red', capstyle='round', dash=20)

    def clear(self):
        self.canvas.delete('all')

from customtkinter import CTkCanvas, CTkFrame, CTkButton
from ...backend.geo_design import Section, Surface, Geometry, Flap, Aileron, Elevator


class GeometryDisplay(CTkFrame):
    """
    A widget for displaying current aircraft's geometry while specifying parameters.

    Attributes:
        geometry (Geometry): Top-level geometry object that is being displayed.
        canvas (CTkCanvas): Canvas widget used for creating the graphic.
        origin (tuple[int, int]): Center point of the display.
        scale (int): A scale used while transforming meters to pixels.
    """

    def __init__(self, parent, geometry: Geometry):
        """
        Parameters:
            parent (CTkFrame): Parent widget to nest the GeometryDisplay instance in.
            geometry (Geometry): Top-level geometry object that is being displayed.
        """
        super().__init__(parent)
        self.geometry = geometry
        self.scale = 100
        self.origin = (0, 0)
        self.canvas = CTkCanvas(self)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.zoom_button = CTkButton(self, text='+', command=self.zoom, width=30, height=30, corner_radius=0)
        self.unzoom_button = CTkButton(self, text='-', command=self.unzoom, width=30, height=30, corner_radius=0)

    def draw(self) -> None:
        """Draws geometry's surfaces and center of mass."""
        self.draw_grid()
        for surface in self.geometry.surfaces.values():
            self.display_wing(surface)
        self.display_CG(*self.geometry.ref_pos[:2])

    def draw_grid(self) -> None:
        """Draws a grid to give a sense of scale."""

        def draw_line(x=None, y=None, thickness=1, color=""):
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            if x is not None: self.canvas.create_line(x, 0, x, height, fill=color, width=thickness)
            if y is not None: self.canvas.create_line(0, y, width, y, fill=color, width=thickness)

        def draw_grid_simple(gap_size, thickness, color="gray90"):
            xi = self.origin[0] % gap_size
            while xi < self.canvas.winfo_width():
                draw_line(x=xi, thickness=thickness, color=color)
                xi += gap_size
            yi = self.origin[1] % gap_size
            while yi < self.canvas.winfo_height():
                draw_line(y=yi, thickness=thickness, color=color)
                yi += gap_size

        meter = self.scale
        draw_grid_simple(.1*meter, 1)
        draw_grid_simple(.5*meter, 2)
        draw_grid_simple(1*meter, 2, color="gray87")
        draw_grid_simple(5*meter, 4, color="gray87")
        draw_grid_simple(10*meter, 4, color="gray80")

    def update(self) -> None:
        """Adjust the display to the window size, redraws everything."""
        self.origin = (self.winfo_width() / 2, self.winfo_height() / 4)
        self.unzoom_button.place(x=self.winfo_width() - 40, y=self.winfo_height() - 40)
        self.zoom_button.place(x=self.winfo_width() - 40, y=self.winfo_height() - 80)
        self.clear()
        self.draw()

    def display_CG(self, x: float, y: float) -> None:
        """Displays a center-of-mass marker at given coordinates."""
        x *= self.scale
        y *= self.scale
        x += self.origin[1]
        y += self.origin[0]
        self.canvas.create_oval(y - 5, x - 5, y + 5, x + 5, fill='yellow')

    def display_section(self, section: Section | list[Section], surface: Surface) -> None:
        """Displays a ``Section`` as a single blue line. If given a list of Sections, displays all."""
        if isinstance(section, list):
            for s in section:
                self.display_section(s, surface)
            return

        assert isinstance(section, Section)

        xle = section.leading_edge_position[0] + surface.origin_position[0]
        yle = section.leading_edge_position[1] + surface.origin_position[1]
        xte = section.trailing_edge_position[0] + surface.origin_position[0]
        self.canvas.create_line(self.origin[0] + yle * self.scale, self.origin[1] + xle * self.scale,
                                self.origin[0] + yle * self.scale, self.origin[1] + xte * self.scale,
                                fill='blue', width=3, capstyle='round', tags='section')
        # mechanisation
        if not section.has_control: return
        x0 = self.origin[1] + (xle + section.control.x_hinge * section.chord) * self.scale -3
        y0 = self.origin[0] + yle * self.scale -3
        self.canvas.create_oval(y0, x0, y0+6, x0+6,
                                outline='black',
                                fill='yellow' if type(section.control) is Flap else 'green')

    def display_wing(self, wing: Surface | list[Surface]) -> None:
        """Displays a ``Surface``. If given a list of Surfaces, displays all."""
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

        sections = list(wing.sections)
        if len(wing.sections) < 2: raise Exception("Can't display a wing with less that 2 sections!")

        self.display_section(sections[0], wing)
        for i in range(1, len(sections)):
            curr_sec = sections[i]
            prev_sec = sections[i - 1]
            self.display_section(curr_sec, wing)

            x0 = self.origin[1] + wing.origin_position[0] * self.scale
            y0 = self.origin[0] + wing.origin_position[1] * self.scale

            # Draw leading edge
            self.canvas.create_line(y0 + prev_sec.leading_edge_position[1] * self.scale,
                                    x0 + prev_sec.leading_edge_position[0] * self.scale,
                                    y0 + curr_sec.leading_edge_position[1] * self.scale,
                                    x0 + curr_sec.leading_edge_position[0] * self.scale,
                                    width=3, fill='black', capstyle='round', tags='edge')
            # Draw trailing edge
            self.canvas.create_line(y0 + prev_sec.trailing_edge_position[1] * self.scale,
                                    x0 + prev_sec.trailing_edge_position[0] * self.scale,
                                    y0 + curr_sec.trailing_edge_position[1] * self.scale,
                                    x0 + curr_sec.trailing_edge_position[0] * self.scale,
                                    width=3, fill='black', capstyle='round', tags='edge')
            # Draw 25% MAC line
            self.canvas.create_line(y0 + prev_sec.leading_edge_position[1] * self.scale,
                                    x0 + (prev_sec.leading_edge_position[0] + prev_sec.chord * .25) * self.scale,
                                    y0 + curr_sec.leading_edge_position[1] * self.scale,
                                    x0 + (curr_sec.leading_edge_position[0] + curr_sec.chord * .25) * self.scale,
                                    width=2, fill='red', capstyle='round', dash=20, tags='edge')

            # Draw control surface, if exists
            if prev_sec.control is None or curr_sec.control is None: continue
            if type(prev_sec.control) is not type(curr_sec.control): continue

            color = {Flap: 'yellow', Aileron: 'green', Elevator: 'green3'}[type(prev_sec.control)]
            x_hinge = prev_sec.control.x_hinge

            y_prev = y0 + prev_sec.leading_edge_position[1] * self.scale
            x_prev_te = x0 + prev_sec.trailing_edge_position[0] * self.scale
            x_prev_le = x_prev_te - (1-x_hinge) * prev_sec.chord * self.scale

            y_curr = y0 + curr_sec.leading_edge_position[1] * self.scale
            x_curr_te = x0 + curr_sec.trailing_edge_position[0] * self.scale
            x_curr_le = x_curr_te - (1-x_hinge) * curr_sec.chord * self.scale

            self.canvas.create_polygon(((y_prev, x_prev_le),
                                        (y_prev, x_prev_te),
                                        (y_curr, x_curr_te),
                                        (y_curr, x_curr_le)),
                                       fill=color, outline='black')

        # Order layers
        self.canvas.tag_raise('control')
        self.canvas.tag_raise('section')
        self.canvas.tag_raise('edge')

    def clear(self) -> None:
        """Clears the current display."""
        self.canvas.delete('all')

    def zoom(self) -> None:
        """Zooms the current display."""
        self.scale *= 1.2
        self.update()

    def unzoom(self) -> None:
        """Unzooms the current display."""
        self.scale /= 1.2
        self.update()

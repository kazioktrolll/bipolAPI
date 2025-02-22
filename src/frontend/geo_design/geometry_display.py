from customtkinter import CTkCanvas, CTkFrame, CTkButton
from tkinter import Event
from enum import IntEnum
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

    # General

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

        self.reset_camera_button = CTkButton(self, text='0', command=self.reset_camera, width=30, height=30, corner_radius=0)

        self.is_dragged = False
        self.drag_origin = (0, 0)
        self.drag_offset = (0, 0)

        self.view_mode = ViewMode.FRONT

    def update(self) -> None:
        """Adjust the display to the window size, redraws everything."""
        self.origin = (self.winfo_width() / 2 + self.drag_offset[0],
                       self.winfo_height() / 4 + self.drag_offset[1])
        self.reset_camera_button.place(x=self.winfo_width() - 40, y=self.winfo_height() - 40)
        self.clear()
        self.draw()

    def project(self, x: float, y: float, z: float) -> tuple[int, int]:
        """Transforms 'real' 3D coordinates into 2D pixel coordinates."""
        match self.view_mode:
            case ViewMode.TOP:
                X = y
                Y = x
            case ViewMode.BOTTOM:
                X = y
                Y = -x
            case ViewMode.LEFT:
                X = x
                Y = -z
            case ViewMode.RIGHT:
                X = -x
                Y = -z
            case ViewMode.FRONT:
                X = -y
                Y = -z
            case ViewMode.BACK:
                X = y
                Y = -z
            case _:
                raise NotImplementedError

        X *= self.scale
        Y *= self.scale
        X += self.origin[0]
        Y += self.origin[1]
        return int(X), int(Y)

    # Displaying

    def draw(self) -> None:
        """Draws geometry's surfaces and center of mass."""
        self.draw_grid()
        for surface in self.geometry.surfaces.values():
            self.display_wing(surface)
        self.display_CG(*self.geometry.ref_pos)

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

    def display_CG(self, x: float, y: float, z: float) -> None:
        """Displays a center-of-mass marker at given coordinates."""
        X, Y = self.project(x, y, z)
        self.canvas.create_oval(X - 5, Y - 5, X + 5, Y + 5, fill='yellow')

    def display_section(self, section: Section | list[Section], surface: Surface) -> None:
        """Displays a ``Section`` as a single blue line. If given a list of Sections, displays all."""
        if isinstance(section, list):
            for s in section:
                self.display_section(s, surface)
            return

        assert isinstance(section, Section)

        xle = section.leading_edge_position[0] + surface.origin_position[0]
        yle = section.leading_edge_position[1] + surface.origin_position[1]
        zle = section.leading_edge_position[2] + surface.origin_position[2]
        xte = section.trailing_edge_position[0] + surface.origin_position[0]
        self.canvas.create_line(self.project(xle, yle, zle),
                                self.project(xte, yle, zle),
                                fill='blue', width=3, capstyle='round', tags='section')
        # mechanisation
        if not section.has_control: return
        x0 = xle + section.control.x_hinge * section.chord
        X, Y = self.project(x0, yle, zle)
        self.canvas.create_oval(X-3, Y-3, X+3, Y+3,
                                outline='black', tags="control",
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

            def globalize(x: float, y: float, z: float) -> tuple[float, float, float]:
                return x + wing.origin_position[0], y + wing.origin_position[1], z + wing.origin_position[2]

            # Draw leading edge
            self.canvas.create_line(self.project(*globalize(*prev_sec.leading_edge_position)),
                                    self.project(*globalize(*curr_sec.leading_edge_position)),
                                    width=3, fill='black', capstyle='round', tags='leading_edge')
            # Draw trailing edge
            self.canvas.create_line(self.project(*globalize(*prev_sec.trailing_edge_position)),
                                    self.project(*globalize(*curr_sec.trailing_edge_position)),
                                    width=3, fill='black', capstyle='round', tags='trailing_edge')
            # Draw 25% MAC line
            self.canvas.create_line(self.project(*globalize(prev_sec.leading_edge_position[0] + prev_sec.chord * .25, *prev_sec.leading_edge_position[1:])),
                                    self.project(*globalize(curr_sec.leading_edge_position[0] + curr_sec.chord * .25, *curr_sec.leading_edge_position[1:])),
                                    width=2, fill='red', capstyle='round', dash=20, tags='mac25')

            # Draw control surface, if exists
            if prev_sec.control is None or curr_sec.control is None: continue
            if type(prev_sec.control) is not type(curr_sec.control): continue

            color = {Flap: 'yellow', Aileron: 'green', Elevator: 'green3'}[type(prev_sec.control)]
            x_hinge = prev_sec.control.x_hinge

            y_prev = prev_sec.leading_edge_position[1]
            x_prev_te = prev_sec.trailing_edge_position[0]
            x_prev_le = x_prev_te - (1-x_hinge) * prev_sec.chord
            z_prev = prev_sec.leading_edge_position[2]

            y_curr = curr_sec.leading_edge_position[1]
            x_curr_te = curr_sec.trailing_edge_position[0]
            x_curr_le = x_curr_te - (1-x_hinge) * curr_sec.chord
            z_curr = curr_sec.leading_edge_position[2]

            self.canvas.create_polygon((self.project(x_prev_le, y_prev, z_prev),
                                        self.project(x_prev_te, y_prev, z_prev),
                                        self.project(x_curr_te, y_curr, z_curr),
                                        self.project(x_curr_le, y_curr, z_curr)),
                                       fill=color, outline='black', tags="control")

        # Order layers
        match self.view_mode:
            case ViewMode.FRONT:
                self.canvas.tag_raise('trailing_edge')
                self.canvas.tag_raise('control')
                self.canvas.tag_raise('section')
                self.canvas.tag_raise('mac25')
                self.canvas.tag_raise('leading_edge')
            case ViewMode.BACK:
                self.canvas.tag_raise('leading_edge')
                self.canvas.tag_raise('mac25')
                self.canvas.tag_raise('section')
                self.canvas.tag_raise('control')
                self.canvas.tag_raise('trailing_edge')
            case mode if mode in [ViewMode.TOP, ViewMode.BOTTOM]:
                self.canvas.tag_raise('control')
                self.canvas.tag_raise('section')
                self.canvas.tag_raise('leading_edge')
                self.canvas.tag_raise('trailing_edge')
                self.canvas.tag_raise('mac25')
            case mode if mode in [ViewMode.LEFT, ViewMode.RIGHT]:
                self.canvas.tag_raise('leading_edge')
                self.canvas.tag_raise('mac25')
                self.canvas.tag_raise('trailing_edge')
                self.canvas.tag_raise('control')
                self.canvas.tag_raise('section')


    def clear(self) -> None:
        """Clears the current display."""
        self.canvas.delete('all')

    # Camera Operations

    def zoom(self) -> None:
        """Zooms the current display."""
        self.scale *= 1.2
        self.update()

    def unzoom(self) -> None:
        """Unzooms the current display."""
        self.scale /= 1.2
        self.update()

    def scroll_zoom(self, event: Event) -> None:
        direction = event.delta // abs(event.delta)
        if direction == -1: self.unzoom()
        elif direction == 1: self.zoom()

    def start_drag(self, event: Event) -> None:
        if event.widget is not self.canvas: return
        self.is_dragged = True
        self.drag_origin = (event.x - self.drag_offset[0],
                            event.y - self.drag_offset[1])

    def stop_drag(self, _) -> None:
        self.is_dragged = False

    def drag(self, event: Event) -> None:
        if not self.is_dragged: return
        self.drag_offset = (event.x - self.drag_origin[0], event.y - self.drag_origin[1])
        self.update()

    def reset_camera(self) -> None:
        self.scale = 100
        self.drag_offset = (0, 0)
        self.update()


class ViewMode(IntEnum):
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4
    FRONT = 5
    BACK = 6
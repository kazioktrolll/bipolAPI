"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkCanvas, CTkFrame, CTkButton
from tkinter import Event
from enum import IntEnum
from ...backend.geo_design import Section, Surface, Geometry
from ...backend import Vector3, handle_crash


class GeometryDisplay(CTkFrame):
    # General

    def __init__(self, parent: CTkFrame):
        """
        Parameters:
            parent (CTkFrame): Parent widget to nest the GeometryDisplay instance in.
        """
        super().__init__(parent)
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

        self.view_mode = ViewMode.ISO

    @property
    def geometry(self) -> Geometry:
        from ...scenes import GeoDesignScene
        assert isinstance(self.master, GeoDesignScene)
        return self.master.geometry

    def update(self) -> None:
        """Adjust the display to the window size, redraws everything."""
        if not self.winfo_exists():
            return

        self.origin = (self.winfo_width() * 4 / 10 + self.drag_offset[0],
                       self.winfo_height() * 6 / 10 + self.drag_offset[1])
        self.reset_camera_button.place(x=10, y=self.winfo_height() - 40)
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
            case ViewMode.ISO:
                X = 3 ** .5 / 2 * x - 3 ** .5 / 2 * y
                Y = .5 * (-x - y) - z
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
        if self.view_mode is not ViewMode.ISO: self.draw_grid()
        for surface in self.geometry.surfaces.values():
            self.display_wing(surface)
        self.display_CG(*self.geometry.ref_pos)
        self.draw_axis()

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
        draw_grid_simple(.1 * meter, 1)
        draw_grid_simple(.5 * meter, 2)
        draw_grid_simple(1 * meter, 2, color="gray87")
        draw_grid_simple(5 * meter, 4, color="gray87")
        draw_grid_simple(10 * meter, 4, color="gray80")

    def draw_axis(self) -> None:
        self.canvas.create_line(self.project(0, 0, 0), self.project(30 / self.scale, 0, 0), arrow='last', fill='red', width=3)
        self.canvas.create_line(self.project(0, 0, 0), self.project(0, 30 / self.scale, 0), arrow='last', fill='green', width=3)
        self.canvas.create_line(self.project(0, 0, 0), self.project(0, 0, 30 / self.scale), arrow='last', fill='blue', width=3)

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

        global_leading_edge_position = section.leading_edge_position + surface.origin_position
        global_trailing_edge_position = section.trailing_edge_position + surface.origin_position
        self.canvas.create_line(self.project(*global_leading_edge_position),
                                self.project(*global_trailing_edge_position),
                                fill='blue', width=3, capstyle='round', tags='section')
        # mechanisation
        if not section.has_control: return
        if section.y == 0 and surface.y_duplicate: return
        X, Y = self.project(*(section.get_position_at_xc(section.control.x_hinge) + surface.origin_position))
        self.canvas.create_oval(X - 3, Y - 3, X + 3, Y + 3,
                                outline='black', tags="control",
                                fill=section.control.color)

    def display_wing(self, wing: Surface | list[Surface]) -> None:
        """Displays a ``Surface``. If given a list of Surfaces, displays all."""
        if wing.disabled: return
        if isinstance(wing, list):
            for w in wing: self.display_wing(w)
            return
        assert isinstance(wing, Surface)

        if wing.y_duplicate:
            # If wing is symmetric, create a mirror copy of the wing,
            # display it, and then continue displaying the original wing.
            ydup = wing.get_symmetric()
            self.display_wing(ydup)

        sections = list(wing.sections)
        if len(wing.sections) < 2: raise Exception("Can't display a wing with less that 2 sections!")

        self.display_section(sections[0], wing)
        for i in range(1, len(sections)):
            curr_sec = sections[i]
            prev_sec = sections[i - 1]
            self.display_section(curr_sec, wing)

            def globalize(pos: Vector3) -> Vector3:
                return pos + wing.origin_position

            # Draw leading edge
            self.canvas.create_line(self.project(*globalize(prev_sec.leading_edge_position)),
                                    self.project(*globalize(curr_sec.leading_edge_position)),
                                    width=3, fill='black', capstyle='round', tags='leading_edge')
            # Draw trailing edge
            self.canvas.create_line(self.project(*globalize(prev_sec.trailing_edge_position)),
                                    self.project(*globalize(curr_sec.trailing_edge_position)),
                                    width=3, fill='black', capstyle='round', tags='trailing_edge')
            # Draw 25% MAC line
            self.canvas.create_line(self.project(*globalize(prev_sec.get_position_at_xc(.25))),
                                    self.project(*globalize(curr_sec.get_position_at_xc(.25))),
                                    width=2, fill='red', capstyle='round', dash=20, tags='mac25')

            # Draw control surface, if exists
            if prev_sec.control is None or curr_sec.control is None: continue
            if not prev_sec.control.is_equal_to(curr_sec.control): continue

            color = prev_sec.control.color
            x_hinge = prev_sec.control.x_hinge

            prev_te = globalize(prev_sec.trailing_edge_position)
            prev_le = globalize(prev_sec.get_position_at_xc(x_hinge))

            curr_te = globalize(curr_sec.trailing_edge_position)
            curr_le = globalize(curr_sec.get_position_at_xc(x_hinge))

            self.canvas.create_polygon((self.project(*prev_le),
                                        self.project(*prev_te),
                                        self.project(*curr_te),
                                        self.project(*curr_le)),
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
            case mode if mode in [ViewMode.TOP, ViewMode.BOTTOM, ViewMode.ISO]:
                self.canvas.tag_raise('control')
                self.canvas.tag_raise('mac25')
                self.canvas.tag_raise('section')
                self.canvas.tag_raise('leading_edge')
                self.canvas.tag_raise('trailing_edge')
            case mode if mode in [ViewMode.LEFT, ViewMode.RIGHT]:
                self.canvas.tag_raise('mac25')
                self.canvas.tag_raise('control')
                self.canvas.tag_raise('section')
                self.canvas.tag_raise('leading_edge')
                self.canvas.tag_raise('trailing_edge')

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
        if direction == -1:
            self.unzoom()
        elif direction == 1:
            self.zoom()

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

    @handle_crash
    def reset_camera(self) -> None:
        self.scale = 100
        self.drag_offset = (0, 0)
        self.update()

    def change_view(self, mode: 'ViewMode') -> None:
        self.view_mode = mode
        self.update()


class ViewMode(IntEnum):
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4
    FRONT = 5
    BACK = 6
    ISO = 7

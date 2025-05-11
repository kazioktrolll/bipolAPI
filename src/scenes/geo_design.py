"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from sys import platform
from functools import cached_property
from .scene import Scene
from ..backend.geo_design import Geometry
from ..frontend import GeometryDisplay, ViewMode, LeftMenu


class GeoDesignScene(Scene):
    @property
    def geometry(self) -> Geometry:
        return self.app.geometry

    @cached_property
    def geometry_display(self):
        return GeometryDisplay(self)

    @cached_property
    def left_menu(self) -> LeftMenu:
        return LeftMenu(self, self.geometry_display.update)

    def build(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.to_update.append(self.geometry_display)
        self.geometry_display.grid(row=0, column=1, sticky='nsew')
        self.geometry_display.draw()

        self.bind_display()

        self.left_menu.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

    def bind_display(self):
        if platform in ("linux", "linux2"):
            self.bind("<Button-4>", lambda e: self.geometry_display.zoom())
            self.bind("<Button-5>", lambda e: self.geometry_display.unzoom())
        else:
            self.bind("<MouseWheel>", self.geometry_display.scroll_zoom)
        self.bind("<Button-1>", self.geometry_display.start_drag)
        # self.bind("<Button-1>", lambda e: print("clicked:", e.widget.cget("text")))
        self.bind("<B1-Motion>", self.geometry_display.drag)
        self.bind("<ButtonRelease-1>", self.geometry_display.stop_drag)
        self.bind("<w>", lambda e: self.geometry_display.change_view(ViewMode.TOP))
        self.bind("<s>", lambda e: self.geometry_display.change_view(ViewMode.FRONT))
        self.bind("<d>", lambda e: self.geometry_display.change_view(ViewMode.RIGHT))
        self.bind("<a>", lambda e: self.geometry_display.change_view(ViewMode.ISO))

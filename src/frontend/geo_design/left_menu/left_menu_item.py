"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkLabel
from typing import Callable, final
from abc import ABC, abstractmethod

from ...parameter_field import ParameterField
from ....backend.geo_design import Surface, Geometry
from ....backend import handle_crash


class LeftMenuItem(CTkFrame, ABC):
    def __init__(self, parent, surface: Surface):
        CTkFrame.__init__(self, parent, fg_color='transparent')
        ABC.__init__(self)
        self.name = surface.name
        self.initialized = False
        self.pfs: dict[str, ParameterField] = {}
        self.disabled = False

        self.pf_frame = CTkFrame(self, fg_color='transparent')
        self.pf_frame.columnconfigure(0, weight=1)

        self.mechanizations = self.LMS.mechanizations
        self.airfoil_chooser = self.LMS.airfoil_chooser

        self.get_all_pfs()
        self.build()
        self.initialized = True

    @property
    @abstractmethod
    def active_pfs(self) -> list[str]:
        ...

    @final
    def __repr__(self) -> str:
        return self.name

    @final
    def build(self) -> None:
        self.update_pfs()
        if not self.mechanizations.grid_info():
            self.mechanizations.grid(row=2, column=0, sticky='nsew', pady=10)
        if not self.airfoil_chooser.grid_info():
            self.airfoil_chooser.grid(row=3, column=0, sticky='nsew', pady=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.pf_frame.grid(row=0, column=0, sticky='nsew')

    @final
    def get_all_pfs(self) -> None:
        surf = self.surface
        data = [
            ('pos', 'Position XZ', 'The X and Z positions of the tip of the root section.',
             lambda tup: True, (surf.origin_position.x, surf.origin_position.z), 'Vector2'),

            ('span', 'Span', "The span of the horizontal tail.\nHas to be positive.",
             lambda w: w > 0, surf.span, 'float'),

            ('chord', 'MAC', "The mean aerodynamic chord of the surface.\nHas to be positive.",
             lambda c: c > 0, surf.mac(), 'float'),

            ('taper', 'Taper Ratio', "The taper ratio of the surface - c_tip / c_root.\nHas to be between 0 and 1.",
             lambda tr: 0 <= tr <= 1, (surf.taper_ratio() if surf.taper_ratio() is not None else 1), 'float'),

            ('sweep', 'Sweep Angle', "Sweep angle of the wing, in degrees.\n"
                                     "The angle between Y-axis and the 25%MAC line. Positive means wing deflected backwards.\n"
                                     "Has to be between -90 and 90.",
             lambda sa: -90 < sa < 90, (surf.sweep_angle() if surf.sweep_angle() is not None else 0), 'float'),

            ('inclination', 'Inclination', "The inclination of the surface, in degrees\n.",
             lambda i: True, surf.sections[0].inclination, 'float'),

            ('dihedral', 'Dihedral', "The dihedral of the surface, in degrees\n.",
             lambda d: -90 < d < 90, surf.sections[0].inclination, 'float'),

            ('surface_area', 'Surface Area', "The area of the surface.\nHas to be positive.",
             lambda s: s > 0, surf.area(), 'float'),

            ('root_chord', 'Root Chord', "The chord of the surface at its root section.",
             lambda c: c > 0, surf.sections[0].chord, 'float'),

            ('mid_chord', 'Mid Chord', "The chord of the surface at the section where it changes the geometry.",
             lambda c: c > 0, surf.mac(), 'float'),#TODO fill

            ('tip_chord', 'Tip Chord', "The chord of the surface at its tip section.",
             lambda c: c > 0, surf.sections[-1].chord, 'float'),

            ('ss', 'Seam Spanwise Position', "The spanwise position of the seam as percent of the wing span.\nHas to be between 0 and 1.",
             lambda ss: 0 < ss < 1, 0.2, 'float'),

            ('height', 'Height', "The height of the vertical tail.\nHas to be positive.",
             lambda h: h > 0, surf.span, 'float'),

            ('gap', 'Gap', "The gap between the two parts of the surface in meters.\n Has to be positive.",
             lambda g: g > 0, 1, 'float'),

        ]

        for d in data:
            kw, n, msg, at, iv, m = d
            self.pfs[kw] = ParameterField(self.pf_frame, name=n, help_message=msg, on_set=self.update_surface, assert_test=at, mode=m)
            self.pfs[kw].set(iv)

    @final
    def update_pfs(self) -> None:
        for name in self.active_pfs:
            if name not in self.pfs.keys():
                raise ValueError(f'No parameter named {name}')

        for i, tup in enumerate(self.pfs.items()):
            name, pf = tup
            if not name in self.active_pfs:
                pf.grid_forget()
            else:
                pf.grid(row=i, column=0, sticky='ew', padx=10, pady=10)

    @abstractmethod
    def update_surface(self, _=None) -> None:
        """Should run super()._update_surface(**kwargs)."""

    @handle_crash
    @final
    def _update_surface(self, surface_creator: Callable[[], Surface]) -> None:

        if not self.initialized: return

        surface = surface_creator()
        surface.set_mechanization(**self.mechanizations.get_values())
        surface.disabled = self.disabled
        self.geometry.replace_surface(surface)
        self.parent.do_on_update()

    @property
    def LMS(self):
        from .left_menu_surface import LeftMenuSurface
        assert isinstance(self.master, LeftMenuSurface)
        return self.master

    @property
    @final
    def parent(self):
        from .left_menu import LeftMenu
        assert isinstance(self.LMS.master, LeftMenu)
        return self.LMS.master

    @property
    @final
    def surface(self) -> Surface:
        return self.geometry.surfaces[self.name]

    @property
    @final
    def geometry(self) -> Geometry:
        return self.parent.geometry


class LMEmpty(LeftMenuItem):
    def __init__(self, parent, surface: Surface):
        super().__init__(parent, surface)
        self.disabled = True
        self.mechanizations.grid_forget()
        self.airfoil_chooser.grid_forget()

    @property
    def active_pfs(self):
        return []

    def update_surface(self, _=None) -> None:
        def getter():
            surf = self.surface.copy()
            surf.clear_mechanization()
            return surf
        super()._update_surface(getter)


class LMOblique(LeftMenuItem):
    def __init__(self, parent, surface: Surface) -> None:
        super().__init__(parent, surface)
        self.mechanizations.grid_forget()
        self.airfoil_chooser.grid_forget()
        self.columnconfigure(0, weight=1)
        CTkLabel(self, text='NOT EDITABLE').grid(row=0, column=0, sticky='nsew')

    @property
    def active_pfs(self):
        return []

    def update_surface(self, _=None) -> None:
        super().update_surface(lambda: self.surface)

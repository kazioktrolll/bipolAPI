"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkLabel, StringVar
from typing import Callable, final, Any, Literal
from abc import ABC, abstractmethod
from functools import cached_property

from ..airfoil_chooser import AirfoilChooser
from ..mechanization_chooser import MechanizationChooser
from ..mechanization_chooser import ControlTypeItem
from ... import FlapItem
from ...parameter_field import ParameterField
from ....backend.geo_design import Surface, Geometry
from ....backend import handle_crash


class LeftMenuItem(CTkFrame, ABC):
    def __init__(self, parent, surface: Surface):
        CTkFrame.__init__(self, parent)
        ABC.__init__(self)
        self.name = surface.name
        self.initialized = False
        self.pfs: dict[str, ParameterField] = {}
        self.disabled = False

        self.pf_frame = CTkFrame(self, fg_color='transparent')
        self.pf_frame.columnconfigure(0, weight=1)

        self.mechanizations = MechanizationChooser(self, self.update_surface, True)
        self.airfoil_chooser = AirfoilChooser(self)
        self.airfoil_chooser.set(surface.airfoil)

        self.init_pfs()
        self.init_mechanization()
        self.build()

    @final
    def __repr__(self) -> str:
        return self.name

    @final
    def build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.pf_frame.grid(row=0, column=0, sticky='nsew')
        self.mechanizations.grid(row=1, column=0, sticky='nsew')
        self.airfoil_chooser.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

    def init_mechanization(self):
        if not self.surface.mechanization: return
        for key, list_of_ranges in self.surface.mechanization.items():
            key = key.capitalize()
            list_preset = ControlTypeItem(key, self.update_surface, True)
            for start, stop, xc in list_of_ranges:
                item = FlapItem()
                item.set_values(StringVar(value=f'{start}'), StringVar(value=f'{stop}'), StringVar(value=f'{xc}'))
                list_preset.add_position(item)
            self.mechanizations.add_position(list_preset)

    @cached_property
    @abstractmethod
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        """keyword, name, message, assert, initial, mode? """
        pass

    @handle_crash
    @final
    def init_pfs(self) -> None:
        for pf_params in self.pfs_params: self._init_pf(*pf_params)
        for pf in self.pfs.values(): pf.name_label.configure(width=100)
        self.initialized = True

    @final
    def _init_pf(self, keyword: str, name: str, message: str, assert_test: Callable[[float], bool], initial_value: float,
                 mode: Literal['bool', 'float', 'Vector2', 'Vector3'] = 'float') -> None:

        if keyword in self.pfs: raise ValueError(f'{keyword} already initialized')
        self.pfs[keyword] = ParameterField(self.pf_frame, name=name, help_message=message, on_set=self.update_surface, assert_test=assert_test, mode=mode)
        self.pfs[keyword].set(initial_value)
        self.pfs[keyword].grid(row=len(self.pfs) - 1, column=0, sticky='e', padx=10, pady=10)

    @abstractmethod
    def update_surface(self, _=None) -> None:
        """Should run super()._update_surface(**kwargs)."""

    @handle_crash
    @final
    def _update_surface(self,
                        surface_creator: Callable[[], Surface] = None,
                        do_with_surface: Callable[[Surface], None] = None
                        ) -> None:
        if surface_creator is None:
            surface_creator = lambda: self.surface

        if not self.initialized: return

        surface = surface_creator()
        if do_with_surface is not None: do_with_surface(surface)
        surface.disabled = self.disabled
        self.geometry.replace_surface(surface)
        self.parent.do_on_update()

    @property
    @final
    def parent(self):
        from .left_menu import LeftMenu
        assert isinstance(self.master.master, LeftMenu)
        return self.master.master

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

    @cached_property
    def pfs_params(self) -> list[tuple[str, str, str, Callable[[Any], bool], Any]]:
        return []

    def update_surface(self, _=None) -> None:
        super()._update_surface()

    def init_mechanization(self): ...


class LMOblique(LMEmpty):
    def __init__(self, parent, surface: Surface) -> None:
        super().__init__(parent, surface)
        self.columnconfigure(0, weight=1)
        CTkLabel(self, text='NOT EDITABLE').grid(row=0, column=0, sticky='nsew')

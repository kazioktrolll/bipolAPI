from customtkinter import CTkFrame
from typing import Callable, final
from abc import ABC, abstractmethod

from .airfoil_chooser import AirfoilChooser
from ..parameter_field import ParameterField
from ..list_preset import ListPreset
from ...backend.geo_design import Surface, Geometry


class LeftMenuItem(CTkFrame, ABC):
    def __init__(self, parent, surface: Surface):
        super().__init__(parent)
        self.pfs: dict[str, ParameterField] = {}
        self.initialized = False
        self.surface = surface

        self.pf_frame = CTkFrame(self, fg_color=self.cget('fg_color'))
        self.pf_frame.columnconfigure(0, weight=1)

        self.mechanizations: dict[str, ListPreset] = {}
        self.mechanizations_frame = CTkFrame(self, fg_color=self.cget('fg_color'))
        self.mechanizations_frame.columnconfigure(0, weight=1)
        self.airfoil_chooser = AirfoilChooser(self)
        self.airfoil_chooser.set(surface.airfoil)

        self.init_pfs()
        self.init_mechanization()

    def __repr__(self) -> str:
        return self.surface.name

    def build(self) -> None:
        for i, mech in enumerate(self.mechanizations.values()):
            mech.grid(row=i, column=0, padx=10, pady=10, sticky='nsew')

        self.columnconfigure(0, weight=1)

        self.pf_frame.grid(row=0, column=0, sticky='nsew')
        self.mechanizations_frame.grid(row=1, column=0, sticky='nsew')
        self.airfoil_chooser.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

    @abstractmethod
    def init_mechanization(self): ...

    @abstractmethod
    def init_pfs(self) -> None:
        """Should define all needed pfs and init them using super()._init_pf(**kwargs), then call super().init_pfs()."""
        for pf in self.pfs.values(): pf.name_label.configure(width=100)
        self.initialized = True

    @final
    def _init_pf(self, keyword: str, name: str, message: str, assert_test: Callable[[float], bool], initial_value: float) -> None:
        if keyword in self.pfs: raise ValueError(f'{keyword} already initialized')
        self.pfs[keyword] = ParameterField(self.pf_frame, name=name, help_message=message, on_set=self.update_surface, assert_test=assert_test)
        self.pfs[keyword].set(initial_value)
        self.pfs[keyword].grid(row=len(self.pfs)-1, column=0, sticky='e', padx=10, pady=10)

    @abstractmethod
    def update_surface(self, _=None) -> None:
        """Should run super()._update_surface(**kwargs)."""

    @final
    def _update_surface(self,
                        surface_creator: Callable[[], Surface],
                        do_with_surface: Callable[[Surface], None] = None
                        ) -> None:
        if not self.initialized: return

        surface = surface_creator()
        if do_with_surface is not None: do_with_surface(surface)
        self.geometry.replace_surface(surface)
        self.parent.do_on_update()

    @property
    @final
    def parent(self):
        from .left_menu import LeftMenu
        assert isinstance(self.master, LeftMenu)
        return self.master

    @property
    def name(self) -> str:
        return self.surface.name

    @property
    @final
    def geometry(self) -> Geometry:
        return self.parent.geometry


class LeftMenuNotImplemented(LeftMenuItem):
    def __init__(self, parent, surface: Surface) -> None:
        super().__init__(parent, surface)

    def init_pfs(self) -> None: ...
    def update_surface(self, _=None) -> None: ...

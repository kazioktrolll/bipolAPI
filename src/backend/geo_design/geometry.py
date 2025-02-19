from typing import Optional
from .surface import Surface


class Geometry:
    """
    A class representing aircraft's geometry.

    Attributes:
        name (str): The name of the aircraft.
        surface_area (float): The surface area of the aircraft.
        chord_length (float): The mean aerodynamic chord length of the aircraft.
        span_length (float): The wingspan of the aircraft.
        mach (float): The cruise speed of the aircraft as Mach number.
        ref_pos (tuple(float, float, float)): The reference position of the aircraft, ideally the position of the center of mass.
        surfaces (Dict[str, Surface]): The ``Surface`` objects associated with the aircraft.
        wing (Surface|None): The wing of the aircraft. Returns 'None' if the aircraft has no defined wing.
    """

    def __init__(self,
                 name: str,
                 chord_length: float,
                 span_length: float,
                 surface_area: float = 0,
                 mach: float = 0,
                 ref_pos: tuple[float, float, float] = (.0, .0, .0)):
        """
        Parameters:
            name (str): The name of the aircraft.
            chord_length (float): The mean aerodynamic chord length of the aircraft.
            span_length (float): The wingspan of the aircraft.
            surface_area (float): The surface area of the aircraft. If not given, will be calculated as chord*span.
            mach (float): The cruise speed of the aircraft as Mach number.
            ref_pos (Tuple[float, float, float]): The reference position of the aircraft, ideally the position of the center of mass.
        """
        self.name = name
        self.mach = mach
        self.chord_length = chord_length
        self.span_length = span_length
        self.surface_area = surface_area or chord_length * span_length
        self.ref_pos = ref_pos
        self.surfaces: dict[str, Surface] = {}

    def add_surface(self, surface: 'Surface') -> None:
        """Add a new surface. The name must be unique."""
        if surface.name in self.surfaces.keys(): raise AttributeError("A surface with name {} already exists.".format(surface.name))
        self.surfaces[surface.name] = surface

    def replace_surface(self, surface: 'Surface') -> None:
        """Replace an existing surface with the new surface."""
        if surface.name not in self.surfaces.keys(): raise AttributeError("No surface named {}.".format(surface.name))
        self.surfaces[surface.name] = surface

    @property
    def wing(self) -> Optional['Surface']:
        """The wing of the aircraft. Returns 'None' if the aircraft has no defined wing."""
        try:
            return self.surfaces["Wing"]
        except KeyError:
            return None

    @property
    def h_tail(self) -> Optional['Surface']:
        """The horizontal tail of the aircraft. Returns 'None' if the aircraft has no defined horizontal tail."""
        try:
            return self.surfaces["H_tail"]
        except KeyError:
            return None

    @property
    def v_tail(self) -> Optional['Surface']:
        """The vertical tail of the aircraft. Returns 'None' if the aircraft has no defined vertical tail."""
        try:
            return self.surfaces["V_tail"]
        except KeyError:
            return None

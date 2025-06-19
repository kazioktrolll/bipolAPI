from .horizontal_surface import HorizontalSurface
from ...section import Section
from ...airfoil import Airfoil
from ...section import Control, Flap, Aileron, Elevator
from ....vector3 import Vector3, AnyVector3
from math import degrees, atan
from typing import Optional


class HorizontalSimpleSurface(HorizontalSurface):
    """ A subclass of the ``Surface`` representing a simple, horizontal, trapezoidal lifting surface. """

    def __init__(self,
                 name: str,
                 span: float,
                 chord_length: float,
                 taper_ratio: float = 1,
                 sweep_angle: float = 0,
                 origin_position: AnyVector3 = Vector3.zero(),
                 inclination_angle: float = 0,
                 airfoil=None,
                 ) -> None:
        """
        Parameters:
            span (float): The span of the surface.
            chord_length (float): The mean aerodynamic chord length of the surface.
            origin_position (AnyVector3): Position of the leading edge of the root chord.
            inclination_angle (float): The inclination of the surface, in degrees.
              Zero means horizontal, positive means leading edge up.
            airfoil (Airfoil): The airfoil of the surface.
            taper_ratio (float): The taper ratio of the surface.
            sweep_angle (float): The sweep angle of the surface in degrees.
        """
        if airfoil is None: airfoil = Airfoil.empty()

        self.taper_ratio = taper_ratio
        self.sweep_angle = sweep_angle
        self.inclination = inclination_angle

        root, tip = HorizontalSimpleSurface.create_geometry(chord_length, span, taper_ratio, sweep_angle,
                                                            inclination_angle, airfoil)
        super().__init__(name=name, sections=[root, tip], y_duplicate=True,
                         origin_position=origin_position, airfoil=airfoil)

        self.mechanization: dict[str, list[tuple[float, float, float]]] = {}

    @classmethod
    def create_geometry(cls, chord_length: float, span: float,
                        taper_ratio: float, sweep_angle: float,
                        inclination: float,
                        airfoil: Airfoil
                        ) -> tuple[Section, Section]:
        """
        Returns the root and tip Sections generated based on input parameters.

        Parameters:
            chord_length (float): The mean aerodynamic chord of the surface.
            span (float): The span of the surface.
            taper_ratio (float): The taper ratio of the surface.
            sweep_angle (float): The sweep angle of the surface in degrees.
            inclination (float): The inclination of the surface, in degrees.
            airfoil (Airfoil): The airfoil of the surface.

        Returns:
            Root and tip Sections, in that order.
        """

        # Calculate position and chord for both root and tip sections.
        root_chord = 2 * chord_length / (1 + taper_ratio)
        chord = lambda y: root_chord * (1 - (1 - taper_ratio) * 2 * y / span)
        from math import radians, tan
        mac025 = lambda y: root_chord * .25 + y * tan(radians(sweep_angle))
        leading_edge_y = lambda y: mac025(y) - chord(y) * .25

        root = Section((0, 0, 0), chord(0), inclination, airfoil)
        tip = Section((leading_edge_y(span / 2), span / 2, 0.0), chord(span / 2),
                      inclination, airfoil)

        return root, tip

    def set_mechanization(self,
                          **kwargs: list[tuple[float, float, float]]
                          ) -> None:
        """Sets the mechanization of the surface.

        Parameters:
            **kwargs (list[tuple[float, float, float]]): For each type of control a tuple (y_start, y_stop, x_hinge).

        Usage:
            surface_instance.set_mechanization(ailerons=[(1, 2, .7), (3, 3.5, .6)], flaps=[(2.1, 2.9, .6)])

            This will create **ailerons** for ``y`` = <1 : 2> ``hinge`` 0.7 x/c and ``y`` = <3 : 3.5> ``hinge`` 0.6 x/c,
            and **flaps** for ``y`` = <2.1 : 2.9> ``hinge`` 0.6 x/c.
        """
        if self.mechanization:
            raise ValueError("The surface {} already has mechanization!".format(self.name))
        self.mechanization = kwargs

        for key, value in kwargs.items():
            key = key.lower()
            for mech_type in [Flap, Aileron, Elevator]:
                if mech_type.is_alias(key):
                    break
            else:
                raise ValueError(f"Unknown mechanism type: {key}")
            # To add a control surface in AVL, you add a control surface to a section,
            # and it is valid up to the next section.
            for start, end, hinge_x in value:
                # Ensure there is a ``Section`` at 'y' == 'start' and 'end'.
                if not self.has_section_at(start): self.add_section_gentle(start)
                if not self.has_section_at(end): self.add_section_gentle(end)
                # Add ``Control`` to every Section between 'start' and 'end'.
                sections = self.get_sections_between(start, end, include_end=True)
                control_instance = mech_type(x_hinge=hinge_x)
                for section in sections:
                    if section.has_control: raise Exception("A section already has a control surface!")
                    section.control = control_instance

            # Check if there are blocks with the same control next to each other,
            # and if so, add a section in between.
            for i, section in enumerate(self.sections):
                if i == 0: continue
                prev_section = self.sections[i - 1]
                if section.control is None: continue
                if section.control.is_equal_to(prev_section.control) and section.control is not prev_section.control:
                    self.add_section_gentle(prev_section.y + 0.01)


    def get_symmetric(self) -> 'HorizontalSimpleSurface':
        """Returns a new instance of HorizontalSimpleSurface reflected about the y-axis."""
        surf = super().get_symmetric()
        assert isinstance(surf, HorizontalSimpleSurface)
        surf.clear_controls()
        surf.mechanization = {}
        sym_controls = {}
        for k, list_of_ranges in self.mechanization.items():
            sym_controls[k] = [(-e, -s, xc) for s, e, xc in list_of_ranges]
        surf.set_mechanization(**sym_controls)
        return surf

    @classmethod
    def from_complex(cls, surface: HorizontalSurface, accuracy=.05, searching = False) -> Optional['HorizontalSimpleSurface']:
        root = surface.sections[0]
        tip = surface.sections[-1]

        leading_edge_x_equation = lambda y: root.x + y / tip.y * (tip.x - root.x)
        leading_edge_z_equation = lambda y: root.z + y / tip.y * (tip.z - root.z)
        chord_equation = lambda y: root.chord + y / tip.y * (tip.chord - root.chord)
        inc = root.inclination

        # Check if the surface is of correct shape
        for section in surface.sections:
            y = section.y
            le = section.leading_edge_position
            c = section.chord
            if abs((le.x - leading_edge_x_equation(y)) / c) > accuracy: return None
            if abs((le.z - leading_edge_z_equation(y)) / c) > accuracy: return None
            if abs((c - chord_equation(y)) / c) > accuracy: return None
            if section.inclination != inc: return None

        tr = tip.chord / root.chord
        sa = degrees(atan(
            (root.get_position_at_xc(.25).x - tip.get_position_at_xc(.25).x) / (tip.y - root.y)
        ))

        simplified = cls(
            surface.name, surface.span(), surface.mac(), tr, sa, surface.origin_position, inc, surface.airfoil
        )

        ## Set Mechanization

        # Add the mechanization
        try:
            controls = HorizontalSimpleSurface._read_controls_from_complex(surface)
            simplified.set_mechanization(**controls)
        except Exception as e:
            if searching:
                return None
            raise e

        return simplified

    @staticmethod
    def _read_controls_from_complex(complex: HorizontalSurface):
        previous_control: Control | None = None
        current_range = [None, None]
        ranges: dict[str, list[tuple[float, float, float]]] = {}

        def start_block(s: Section) -> tuple[Control, list[int]]:
            return s.control, [s.y, None]

        def break_block():
            # If the previous control is None, there is no block to break.
            if previous_control is None: return
            # If this is the first block of this type, create a list for it.
            name = previous_control.name
            if name not in ranges.keys(): ranges[name] = []
            # Append the dict by this block.
            if None in current_range: raise ValueError
            ranges[name].append((current_range[0], current_range[1], previous_control.x_hinge))

        for section in complex.sections:
            # If this section has the same control as the previous, extend block and continue.
            if section.control and section.control.is_equal_to(previous_control):
                current_range[1] = section.y
                continue
            # Now we know that the block needs to be broken
            break_block()

            # If this section has a new control, start a new block
            if section.control is not None:
                previous_control, current_range = start_block(section)
        # Break the last block
        break_block()

        return ranges

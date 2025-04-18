from typing import Callable, TypeVar, Generic
from customtkinter import CTkFrame, CTkLabel, DoubleVar, StringVar, CTkEntry, CTkButton, CTkFont, CTkOptionMenu
from abc import ABC, abstractmethod
from .parameter_field import HelpTopLevel
from .popup import Popup
from ..backend import Vector3
from ..backend.geo_design import Control, Section


T = TypeVar('T', bound=tuple)


class Item(ABC, Generic[T]):
    @abstractmethod
    def edit(self, display_update: Callable[[], None]) -> None: pass
    @abstractmethod
    def get_values(self) -> T: pass
    @abstractmethod
    def display(self, parentL: CTkFrame) -> CTkFrame: pass


class FlapItem(Item[tuple[float, float, float]]):
    def __init__(self):
        self.start = DoubleVar(value=0)
        self.end = DoubleVar(value=0)
        self.xc = DoubleVar(value=0)

    def edit(self, do_on_update: Callable[[], None]):
        window = Popup(master=None)

        startvar = StringVar(value=str(self.start.get()))
        endvar = StringVar(value=str(self.end.get()))
        xcvar = StringVar(value=str(self.xc.get()))

        if startvar.get() == "0.0" and endvar.get() == "0.0" and xcvar.get() == "0.0":
            startvar.set("")
            endvar.set("")
            xcvar.set("")

        window.columnconfigure(1, minsize=5)

        CTkLabel(window.frame, text="Specify geometry of the device", font=CTkFont(weight='bold')
                 ).grid(column=0, row=0, columnspan=3, sticky='nsew', padx=5, pady=5)

        CTkLabel(window.frame, text="start:"
                 ).grid(column=0, row=1, sticky="e")
        CTkEntry(window.frame, textvariable=startvar
                 ).grid(column=2, row=1, sticky='nsew')

        CTkLabel(window.frame, text="end: "
                 ).grid(column=0, row=2, sticky="e")
        CTkEntry(window.frame, textvariable=endvar
                 ).grid(column=2, row=2, sticky='nsew')

        CTkLabel(window.frame, text="xc: "
                 ).grid(column=0, row=3, sticky="e")
        CTkEntry(window.frame, textvariable=xcvar
                 ).grid(column=2, row=3, sticky='nsew')

        CTkButton(window.frame, text='?', width=25, height=25,
                  command=lambda: HelpTopLevel(None, message="Input new parameters of the device.\n"
                                                               "start, stop: y-coordinate of the "
                                                               "start and the end of the device. "
                                                               "Start must be closer to the main axis of the aircraft, "
                                                               "while stop must be closer to the wing tip.\n"
                                                               "xc: chord-wise position of the hinge as a percentage "
                                                               "of the chord. Must be between 0 and 1.",
                                               max_width=40)
                  ).grid(column=0, row=4, columnspan=2, sticky='nsew')

        CTkButton(window.frame, text="Set",
                  command=lambda: (self.set_values(startvar, endvar, xcvar),
                                   window.destroy(),
                                   do_on_update())
                  ).grid(column=2, row=4, sticky='nsew')

        window.run()

    def set_values(self, start: StringVar, end: StringVar, xc: StringVar) -> None:
        try:
            start = float(start.get())
            end = float(end.get())
            xc = float(xc.get())
        except ValueError: return
        if not abs(start) <= abs(end): return
        if not 0 < xc < 1: return
        self.start.set(start)
        self.end.set(end)
        self.xc.set(xc)

    def get_values(self) -> tuple[float, float, float]:
        return self.start.get(), self.end.get(), self.xc.get()

    def display(self, parent: CTkFrame) -> CTkFrame:

        class FlapDisplay(CTkFrame):
            def __init__(self, item: 'FlapItem', parent: CTkFrame):
                CTkFrame.__init__(self, parent, fg_color=parent.cget('fg_color'))
                self.item = item

                CTkLabel(self, text="start: "
                         ).grid(column=0, row=0)
                CTkLabel(self, textvariable=item.start, width=30, anchor='w'
                         ).grid(column=1, row=0)

                CTkLabel(self, text="end: "
                         ).grid(column=2, row=0)
                CTkLabel(self, textvariable=item.end, width=30, anchor='w'
                         ).grid(column=3, row=0)

                CTkLabel(self, text="xc: "
                         ).grid(column=4, row=0)
                CTkLabel(self, textvariable=item.xc, width=10, anchor='w'
                         ).grid(column=5, row=0)

                self.update()

            def update(self) -> None:
                if self.item.start.get() == 0 and self.item.end.get() == 0:
                    self.disable()
                    return
                self.enable()

            def disable(self):
                for child in self.children.values():
                    if not isinstance(child, CTkLabel): continue
                    child.configure(text_color='gray30')

            def enable(self):
                for child in self.children.values():
                    if not isinstance(child, CTkLabel): continue
                    child.configure(text_color='white')

        return FlapDisplay(item=self, parent=parent)


class SectionItem(Item[tuple[Vector3, float, float, Control|None]]):
    def __init__(self, left_menu):
        self._left_menu = left_menu
        self.x = DoubleVar(value=0)
        self.y = DoubleVar(value=0)
        self.z = DoubleVar(value=0)
        self.chord = DoubleVar(value=0.0)
        self.inclination = DoubleVar(value=0.0)
        self.control: Control | None = None

    @property
    def left_menu(self):
        from .geo_design.left_menu_item import LeftMenuItem
        assert isinstance(self._left_menu, LeftMenuItem)
        return self._left_menu

    @classmethod
    def from_section(cls, section: Section, left_menu) -> 'SectionItem':
        _r = SectionItem(left_menu)
        _r.x.set(section.x)
        _r.y.set(section.y)
        _r.z.set(section.z)
        _r.chord.set(section.chord)
        _r.inclination.set(section.inclination)
        _r.airfoil = section.airfoil
        _r.control = section.control
        return _r

    @property
    def position(self): return Vector3(self.x.get(), self.y.get(), self.z.get())

    def edit(self, do_on_update: Callable[[], None]) -> None:
        window = Popup(master=None)

        xvar = StringVar(value=str(self.x.get()))
        yvar = StringVar(value=str(self.y.get()))
        zvar = StringVar(value=str(self.z.get()))
        chordvar = StringVar(value=str(self.chord.get()))
        incvar = StringVar(value=str(self.inclination.get()))

        window.frame.columnconfigure(1, minsize=5)

        CTkLabel(window.frame, text="Specify parameters of the section", font=CTkFont(weight='bold')
                 ).grid(column=0, row=0, columnspan=3, sticky='nsew', padx=5, pady=5)

        CTkLabel(window.frame, text="x: "
                 ).grid(column=0, row=2, sticky="e")
        CTkEntry(window.frame, textvariable=xvar
                 ).grid(column=2, row=2, sticky='nsew')

        CTkLabel(window.frame, text="y: "
                 ).grid(column=0, row=3, sticky="e")
        CTkEntry(window.frame, textvariable=yvar
                 ).grid(column=2, row=3, sticky='nsew')

        CTkLabel(window.frame, text="z: "
                 ).grid(column=0, row=4, sticky="e")
        CTkEntry(window.frame, textvariable=zvar
                 ).grid(column=2, row=4, sticky='nsew')

        CTkLabel(window.frame, text="chord: "
                 ).grid(column=0, row=5, sticky="e")
        CTkEntry(window.frame, textvariable=chordvar
                 ).grid(column=2, row=5, sticky='nsew')

        CTkLabel(window.frame, text="inclination: "
                 ).grid(column=0, row=6, sticky="e")
        CTkEntry(window.frame, textvariable=incvar
                 ).grid(column=2, row=6, sticky='nsew')

        CTkLabel(window.frame, text="Control: "
                 ).grid(column=0, row=7, sticky="e")
        controls_available = self.left_menu.mechanizations.get_values()
        values = ['None'] + list(controls_available.keys())
        control_picker = CTkOptionMenu(window.frame, values=values)
        if self.control:
            control_picker.set(self.control.name.capitalize())
        control_picker.grid(column=2, row=7, sticky='nsew')

        CTkButton(window.frame, text='?', width=25, height=25,
                  command=lambda: HelpTopLevel(None, message="Input new parameters of the device.\n"
                                                             "start, stop: y-coordinate of the "
                                                             "start and the end of the device. "
                                                             "Start must be closer to the main axis of the aircraft, "
                                                             "while stop must be closer to the wing tip.\n"
                                                             "xc: chord-wise position of the hinge as a percentage "
                                                             "of the chord. Must be between 0 and 1.",
                                               max_width=40)
                  ).grid(column=0, row=8, columnspan=2, sticky='nsew')

        CTkButton(window.frame, text="Set",
                  command=lambda: (self.set_values(xvar, yvar, zvar, chordvar, incvar, control_picker.get()),
                                   window.destroy(),
                                   do_on_update())
                  ).grid(column=2, row=8, sticky='nsew')

        window.run()

    def set_values(self, x: StringVar, y: StringVar, z: StringVar, chord: StringVar, inc: StringVar, ctrl: str) -> None:
        try:
            x = float(x.get())
            y = float(y.get())
            z = float(z.get())
            chord = float(chord.get())
            inc = float(inc.get())
        except ValueError: return
        if chord <= 0: return
        self.x.set(x)
        self.y.set(y)
        self.z.set(z)
        self.chord.set(chord)
        self.inclination.set(inc)
        if ctrl == 'None':
            self.control = None
        else:
            vals = self.left_menu.mechanizations.get_values()
            val = vals[ctrl]
            self.control = val

    def get_values(self) -> tuple[Vector3, float, float, Control|None]:
        return self.position, self.chord.get(), self.inclination.get(), self.control

    def display(self, parent: CTkFrame) -> CTkFrame:

        class SectionDisplay(CTkFrame):
            def __init__(self, item: SectionItem, parent: CTkFrame):
                CTkFrame.__init__(self, parent, fg_color=parent.cget('fg_color'))
                self.item = item

                CTkLabel(self, text="position: "
                         ).grid(column=0, row=0)
                CTkLabel(self, textvariable=item.x, width=10, anchor='w'
                         ).grid(column=1, row=0)
                CTkLabel(self, textvariable=item.y, width=10, anchor='w'
                         ).grid(column=2, row=0)
                CTkLabel(self, textvariable=item.z, width=10, anchor='w'
                         ).grid(column=3, row=0)

                CTkLabel(self, text="chord: "
                         ).grid(column=0, row=1)
                CTkLabel(self, textvariable=item.chord, width=30, anchor='w'
                         ).grid(column=1, row=1)

                CTkLabel(self, text="inclination: "
                         ).grid(column=2, row=1)
                CTkLabel(self, textvariable=item.inclination, width=30, anchor='w'
                         ).grid(column=3, row=1)

                self.update()

        return SectionDisplay(item=self, parent=parent)

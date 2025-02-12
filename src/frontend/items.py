from typing import Callable
from customtkinter import CTkFrame, CTkLabel, DoubleVar, StringVar, CTkToplevel, CTkEntry, CTkButton
from abc import ABC, abstractmethod
from .parameter_field import HelpTopLevel
from .popup import Popup


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


class Item(ABC):
    @abstractmethod
    def edit(self, display_update: Callable[[], None]) -> None: pass
    @abstractmethod
    def get_values(self) -> tuple: pass
    @abstractmethod
    def display(self, parentL: CTkFrame) -> CTkFrame: pass


class FlapItem(Item):
    def __init__(self):
        super().__init__()
        self.start = DoubleVar(value=0)
        self.end = DoubleVar(value=0)
        self.xc = DoubleVar(value=0)

    def edit(self, do_on_update: Callable[[], None]):
        window = Popup(master=None, title="Edit")

        startvar = StringVar(value=str(self.start.get()))
        endvar = StringVar(value=str(self.end.get()))
        xcvar = StringVar(value=str(self.xc.get()))

        window.columnconfigure(1, minsize=10)

        CTkLabel(window, text="start:"
                 ).grid(column=0, row=0)
        CTkEntry(window, textvariable=startvar
                 ).grid(column=2, row=0)

        CTkLabel(window, text="end: "
                 ).grid(column=0, row=1)
        CTkEntry(window, textvariable=endvar
                 ).grid(column=2, row=1)

        CTkLabel(window, text="xc: "
                 ).grid(column=0, row=2)
        CTkEntry(window, textvariable=xcvar
                 ).grid(column=2, row=2)

        CTkButton(window, text='?', width=25, height=25,
                  command=lambda: HelpTopLevel(None, message="Input new parameters of the device.\n"
                                                               "start, stop: y-coordinate of the "
                                                               "start and the end of the device. "
                                                               "Start must be closer to the main axis of the aircraft, "
                                                               "while stop must be closer to the wing tip.\n"
                                                               "xc: chord-wise position of the hinge as a percentage "
                                                               "of the chord. Must be between 0 and 1.",
                                               max_width=40)
                  ).grid(column=0, row=3, columnspan=2, sticky='nsew')

        CTkButton(window, text="Set",
                  command=lambda: (self.set_values(float(startvar.get()), float(endvar.get()), float(xcvar.get())),
                                   window.destroy(),
                                   do_on_update())
                  ).grid(column=2, row=3, sticky='nsew')

        window.run()

    def set_values(self, start: float, end: float, xc: float) -> None:
        if not abs(start) <= abs(end): return
        if not 0 < xc < 1: return
        self.start.set(start)
        self.end.set(end)
        self.xc.set(xc)

    def get_values(self) -> tuple[float, float, float]:
        return self.start.get(), self.end.get(), self.xc.get()

    def display(self, parent: CTkFrame) -> CTkFrame:
        return FlapDisplay(item=self, parent=parent)
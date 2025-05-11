from typing import Callable
from customtkinter import CTkFrame, CTkLabel, CTkOptionMenu, CTkButton
from ..list_preset import ListPreset
from ..items import Item, FlapItem
from ..popup import Popup
from ...backend.geo_design import Control


class MechanizationChooser(ListPreset):
    def __init__(self, parent: CTkFrame, do_on_update: Callable[[], None], define_ranges: bool):
        super().__init__(parent, 'Control Surfaces', ControlTypeItem, do_on_update)
        self.lists: dict[str, ControlTypeItem] = {}
        self.controls: dict[str, Control] = {}
        self.define_ranges = define_ranges
        # Initialization should be specified not in this class,
        # but in appropriate LeftMenu class, as it will be different
        # depending on the type of the lifting surface being represented.

    def add_position(self, item: 'ControlTypeItem' = None) -> None:
        """Adds an existing item or creates a new one by asking the user."""
        if item is None:
            self.add_by_user()
        else:
            self.add_by_item(item)

    def add_by_item(self, item: 'ControlTypeItem') -> None:
        """Adds a display object to self. If no object given, opens dialog for user to create one."""
        key = item.control_type_name
        if key in self.lists.keys(): return
        super().add_position(item)
        self.item_frames[-1].children['!ctkbutton'].grid_forget()
        self.lists[key] = item

    def add_by_user(self):
        """Opens a dialog for user to create a new type."""
        vals = [val for val in ['Ailerons', 'Flaps', 'Elevators'] if val not in self.lists.keys()]
        if not vals: return

        window = Popup(master=None)
        CTkLabel(window, text='Type:').grid(column=0, row=1, padx=10, pady=10)
        om = CTkOptionMenu(window.frame, values=vals)
        om.grid(column=1, row=1)

        def confirm():
            val = om.get()
            window.destroy()
            self.add_by_type(val)

        CTkButton(window.frame, text='Confirm', command=confirm
                  ).grid(column=0, row=2, columnspan=2, sticky='nsew', padx=10, pady=10)
        window.run()

    def add_by_type(self, ctrl_type: str):
        """Creates a display for a new control surface type."""
        if ctrl_type in self.lists.keys(): return
        item = ControlTypeItem(ctrl_type, self.do_on_update, self.define_ranges)
        self.add_by_item(item)
        self.lists[ctrl_type] = item

    def add_by_control(self, control: Control):
        self.controls[control.name] = control
        self.add_by_type(control.name.capitalize())

    def get_values(self) -> dict[str, list] | dict[str, Control]:
        if not self.define_ranges: return self.controls
        return {name: lp.get_values() for name, lp in self.lists.items()}


class ControlTypeItem(ListPreset, Item):
    def __init__(self, ctrl_type: str, do_on_update: Callable[[], None], define_ranges: bool):
        self.control_type_name = ctrl_type
        self.lp_do_on_update = do_on_update
        self.define_ranges = define_ranges
        Item.__init__(self)
        ListPreset.__init__(self, None, self.control_type_name, FlapItem, do_on_update)

    def edit(self, display_update: Callable[[], None]):
        ...

    def get_values(self) -> list[tuple]:
        if not self.define_ranges: return []
        return ListPreset.get_values(self)

    def display(self, parentL: CTkFrame) -> CTkFrame:
        if not self.define_ranges:
            f = CTkFrame(parentL, fg_color='transparent', width=0, height=0)
            CTkLabel(f, text=self.control_type_name, fg_color='transparent').pack()
            return f
        ListPreset.init_display(self, parentL)
        return self.main_frame

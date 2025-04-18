from typing import Callable
from customtkinter import CTkFrame, CTkLabel, CTkOptionMenu, CTkButton
from ..list_preset import ListPreset
from ..items import Item, FlapItem
from ..popup import Popup


class MechanizationChooser(ListPreset):
    def __init__(self, parent: CTkFrame, do_on_update: Callable[[], None]):
        super().__init__(parent, 'Control Surfaces', ControlTypeItem, do_on_update)
        self.lists = {}
        # Initialization should be specified not in this class,
        # but in appropriate LeftMenu class, as it will be different
        # depending on the type of the lifting surface being represented.

    def add_position(self, item: 'ControlTypeItem' = None) -> None:
        """Adds an existing item or creates a new one by asking the user."""
        if item is None:
            self.add_new_type_by_user()
        else:
            self.add_by_item(item)

    def add_by_item(self, item: 'ControlTypeItem') -> None:
        """Adds a display object to self. If no object given, opens dialog for user to create one."""
        key = item.category_name
        if key in self.lists.keys(): return
        super().add_position(item)
        self.item_frames[-1].children['!ctkbutton'].grid_forget()
        self.lists[key] = item

    def add_new_type_by_user(self):
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
        item = ControlTypeItem(ctrl_type, self.do_on_update)
        self.add_by_item(item)
        self.lists[ctrl_type] = item

    def get_values(self):
        return {name: lp.get_values() for name, lp in self.lists.items()}


class ControlTypeItem(ListPreset, Item):
    def __init__(self, ctrl_type: str, do_on_update: Callable[[], None]):
        self.control_type_name = ctrl_type
        self.lp_do_on_update = do_on_update
        Item.__init__(self)
        ListPreset.__init__(self, None, self.control_type_name, FlapItem, do_on_update)   #TODO: tutaj

    def edit(self, display_update: Callable[[], None]): ...

    def get_values(self) -> list[tuple]:
        return ListPreset.get_values(self)

    def display(self, parentL: CTkFrame) -> CTkFrame:
        ListPreset.init_display(self, parentL)
        return self.main_frame

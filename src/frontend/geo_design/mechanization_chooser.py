from typing import Callable
from customtkinter import CTkFrame, CTkLabel, CTkOptionMenu, CTkButton
from ..list_preset import ListPreset
from ..items import Item, FlapItem
from ..popup import Popup


class MechanizationChooser(ListPreset):
    def __init__(self, parent: CTkFrame, do_on_update: Callable[[], None]):
        super().__init__(parent, 'Control Surfaces', ListPresetItem, do_on_update)
        self.lists = {}

    def add_position(self, key_item: tuple[str, 'ListPresetItem']=None) -> None:
        key, item = key_item or (None, None)
        if key in self.lists.keys(): return
        if item:
            super().add_position(item)
            self.item_frames[-1].children['!ctkbutton'].grid_forget()
            self.lists[key] = item
            return
        window = Popup(master=None)
        CTkLabel(window, text='Type:').grid(column=0, row=1, padx=10, pady=10)
        vals = [val for val in ['Ailerons', 'Flaps', 'Elevators'] if val not in self.lists.keys()]
        if not vals:
            window.destroy()
            return
        om = CTkOptionMenu(window, values=vals)
        om.grid(column=1, row=1)

        def confirm():
            val = om.get()
            window.destroy()
            self.create_new(val)

        CTkButton(window, text='Confirm', command=confirm).grid(column=0, row=2, columnspan=2, sticky='nsew', padx=10, pady=10)
        window.run()

    def create_new(self, item_type: str):
        item = ListPresetItem(item_type, self.do_on_update)
        self.add_position((item_type, item))
        self.lists[item_type] = item

    def get_values(self):
        return {name: lp.get_values() for name, lp in self.lists.items()}


class ListPresetItem(ListPreset, Item):
    def __init__(self, name: str, do_on_update: Callable[[], None]):
        self.lp_name = name
        self.lp_do_on_update = do_on_update
        Item.__init__(self)
        ListPreset.__init__(self, None, self.lp_name, FlapItem, do_on_update)

    def edit(self, display_update: Callable[[], None]): ...

    def get_values(self) -> list[tuple]:
        return ListPreset.get_values(self)

    def display(self, parentL: CTkFrame) -> CTkFrame:
        ListPreset.init_display(self, parentL)
        return self.main_frame

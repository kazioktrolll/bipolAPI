# from src.app import App
# from src.scenes import GeoDesignScene
# from src.backend.geo_design import GeometryGenerator
#
#
# app = App()
# app.geometry = GeometryGenerator.default()
# app.set_scene(GeoDesignScene(app))
# app.run()
#
#   ----------------------------------------------
#
# from src.calcs import App
#
#
# def load():
#     from pathlib import Path
#     path = Path(r"C:\Users\kazio\Downloads\test_working.gavl")
#     import pickle
#     with open(path, 'rb') as f:
#         return pickle.load(f)
#
#
# app = App(load())
# app.run()
#
#   -------------------------------------------
#
from src.calcs import OperInput
from customtkinter import CTk, CTkButton


root = CTk()
ois = [OperInput.by_template(root, t, root, i) for i, t in enumerate(['a', 'b', 'r', 'p', 'y'])]
def get_comm_strs():
    for oi in ois: print(oi.command_string())
CTkButton(root, text='Print', command=get_comm_strs).grid(row=10, column=0, columnspan=6)
root.mainloop()
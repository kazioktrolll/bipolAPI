from .scene import Scene


class SceneAvlMain(Scene):
    def __init__(self, master):
        from ..Widgets import HoverButton

        super().__init__(master)
        buttons = {
        "oper": print("oper"),
        "mode" : print("mode"),
        "time": print("time"),
        
        "load f": print("load f"),
        "mass f": print("mass f"),
        "case f": print("case f"),
        
        "cini": print("cini"),
        "mset": print("mset"),
        
        "plop": print("plop"),
        "name": print("name")
        }
        for i, (k, v) in enumerate(buttons.items()):
            self.grid_rowconfigure(i, weight=0)
            HoverButton(self, text=k, hover_text="No Description", command=v).grid(row=i, column=0)
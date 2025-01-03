from .scene import Scene


class SceneAvlMain(Scene):
    def __init__(self, master):
        from ..Widgets import HoverButton

        super().__init__(master)
        buttons = {
        "oper": lambda: print("oper"),
        "mode" : lambda: print("mode"),
        "time": lambda: print("time"),
        
        "load f": lambda: print("load f"),
        "mass f": lambda: print("mass f"),
        "case f": lambda: print("case f"),
        
        "cini": lambda: print("cini"),
        "mset": lambda: print("mset"),
        
        "plop": lambda: print("plop"),
        "name": lambda: print("name")
        }
        for i, (k, v) in enumerate(buttons.items()):
            self.grid_rowconfigure(i, weight=0)
            HoverButton(
                self, text=k, hover_text="No Description", command=v
            ).grid(row=i, column=0)
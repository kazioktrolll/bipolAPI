from .handler import Handler, open_process


xfoil_path = r"D:\Program Files\XFOIL6.99\xfoil.exe"


def xfoil():
    return open_process(xfoil_path)


class Xfoil_handler(Handler):
    def __init__(self, app):
        from ..Scenes import Scene
        super().__init__(app, xfoil_path)
        self.change_to_scene(Scene)
        self.scene.configure(fg_color="green")

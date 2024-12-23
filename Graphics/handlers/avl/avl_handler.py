from ..handler import Handler, open_process
from.main_scene import AvlMainScene


avl_path = r"C:\Users\kazio\OneDrive\Pulpit\BIPOL\avl.exe"


class Avl_handler(Handler):
    def __init__(self):
        super().__init__(avl_path)
        self.main_scene = AvlMainScene(self)
        self.current_scene = self.main_scene


def avl():
    return open_process(avl_path)
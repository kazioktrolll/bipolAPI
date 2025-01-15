from .handler import Handler
from ..Scenes import SceneAvlInitial


avl_path = r"C:\Users\kazio\OneDrive\Pulpit\BIPOL\avl.exe"


class Avl_handler(Handler):
    def __init__(self, app):
        super().__init__(app, avl_path)
        self.change_to_scene(SceneAvlInitial)
        self.current_file = ""

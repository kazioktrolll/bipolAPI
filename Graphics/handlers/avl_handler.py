from .handler import Handler
from ..Scenes import SceneAvlInitial


avl_path = r"C:\Users\kazio\OneDrive\Pulpit\BIPOL\avl.exe"


class Avl_handler(Handler):
    def __init__(self, app):
        super().__init__(avl_path)
        self.scene = SceneAvlInitial(app)
        self.current_file = ""

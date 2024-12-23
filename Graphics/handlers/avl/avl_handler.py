from ..handler import Handler
from ...app import App


avl_path = r"C:\Users\kazio\OneDrive\Pulpit\BIPOL\avl.exe"


class Avl_handler(Handler):
    def __init__(self, app:App):
        from.main_scene import AvlMainScene

        super().__init__(app, avl_path)
        self.main_scene = AvlMainScene(self.app)
        self.current_scene = self.main_scene

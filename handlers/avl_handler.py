from .handler import Handler


avl_path = r"C:\Users\kazio\OneDrive\Pulpit\BIPOL\avl.exe"


class Avl_handler(Handler):
    def __init__(self):
        super().__init__(avl_path)


from .handler import Handler, open_process


xfoil_path = r"D:\Program Files\XFOIL6.99\xfoil.exe"


def xfoil():
    return open_process(xfoil_path)


class Xfoil_handler(Handler):
    def __init__(self):
        super().__init__(xfoil_path)
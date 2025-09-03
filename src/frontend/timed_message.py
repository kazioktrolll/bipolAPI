from customtkinter import CTkFrame, CTkLabel


class TimedMessage:
    def __init__(self, parent, text: str, duration: float = 1.0):
        self.frame = CTkFrame(parent)
        self.frame.pack_propagate(True)
        CTkLabel(self.frame, text=text).pack(padx=10, pady=10)
        self._duration = duration

    def run(self):
        self.frame.lift()
        self.frame.after(int(self._duration * 1000), self.frame.destroy) # noqa

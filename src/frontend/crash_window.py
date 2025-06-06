from customtkinter import CTk, CTkTextbox

class CrashWindow(CTk):
    def __init__(self, error: str):
        super().__init__()
        # Create a read-only textbox that looks like a label
        scrollable_label = CTkTextbox(self, width=380, height=180, wrap="word")
        scrollable_label.pack(padx=10, pady=10, fill="both", expand=True)

        scrollable_label.insert("0.0", error)
        scrollable_label.configure(state="disabled")  # Make it read-only

        self.update()
        self.after(100, self.geometry, "")
        self.mainloop()
import customtkinter as ctk

class HoverButton(ctk.CTkFrame):
    def __init__(self, master, text, hover_text, command, **kwargs):
        super().__init__(master, **kwargs)
        colour = ctk.CTkButton(None).cget("fg_color")
        self.configure(fg_color=colour)

        self.command = command
        self.hover_timer = None

        # Button label
        self.button_label = ctk.CTkLabel(self, text=text, fg_color=colour)
        self.button_label.pack(fill="both", expand=True, padx=5, pady=5)

        # Hover label
        self.hover_label = ctk.CTkLabel(self.master, text=hover_text, fg_color="gray75", text_color="black")
        self.hover_label.place_forget()

        # Bind hover events
        self.button_label.bind("<Enter>", self.start_hover_timer)
        self.button_label.bind("<Leave>", self.cancel_hover)
        self.button_label.bind("<Button-1>", self.on_click)

    def start_hover_timer(self, event):
        if self.hover_label.cget("text") == "":
            return
        # Start a timer to show the hover text after 1 second
        from threading import Timer
        self.hover_timer = Timer(1.0, self.show_hover_text, [event])
        self.hover_timer.start()

    def cancel_hover(self, event):
        if self.hover_label.cget("text") == "":
            return
        # Cancel the hover timer and hide the hover label
        if self.hover_timer:
            self.hover_timer.cancel()
            self.hover_timer = None
        self.hover_label.place_forget()

    def show_hover_text(self, event):
        # Calculate button's bottom right corner position
        button_x = self.winfo_rootx() - self.master.winfo_rootx()
        button_y = self.winfo_rooty() - self.master.winfo_rooty()
        button_width = self.winfo_width()
        button_height = self.winfo_height()

        self.hover_label.place(x=button_x + button_width, y=button_y + button_height)

    def on_click(self, event):
        if self.command:
            self.command()


if __name__ == "__main__":
    # Example usage
    def button_action():
        print("Button clicked!")

    app = ctk.CTk()
    app.geometry("400x200")

    hover_button = HoverButton(app, text="Click Me", hover_text="Additional Info", command=button_action)
    hover_button.pack(pady=20, padx=20)

    app.mainloop()

# TODO: make it so the label is always visible and doesn't render outside of the window.

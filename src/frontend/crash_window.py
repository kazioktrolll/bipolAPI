"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTk, CTkTextbox, CTkLabel


class CrashWindow(CTk):
    def __init__(self, error: str):
        super().__init__()
        CTkLabel(self,
                 text='A critical error has occurred.\nPlease send the error message along with your .gavl file\nto Support at issues.gavl@gmail.com\n'
                 ).pack(padx=10, pady=10)
        # Create a read-only textbox that looks like a label
        scrollable_label = CTkTextbox(self, width=380, height=180, wrap="word")
        scrollable_label.pack(padx=10, pady=10, fill="both", expand=True)

        scrollable_label.insert("0.0", error)
        scrollable_label.configure(state="disabled")  # Make it read-only

        self.update()
        self.after(100, self.geometry, "")
        self.mainloop()
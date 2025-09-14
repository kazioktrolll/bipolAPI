"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import sys
import traceback

from customtkinter import CTk, CTkTextbox, CTkLabel


class CrashWindow:
    def __init__(self, error: str):
        root = CTk()
        self._root = root
        super().__init__()
        CTkLabel(root,
                 text='A critical error has occurred.\n'
                      'Please send the error message along with your .gavl file\n'
                      'to Support at issues.gavl@gmail.com\n'
                 ).pack(padx=10, pady=10)
        # Create a read-only textbox that looks like a label
        scrollable_label = CTkTextbox(root, width=1000, height=400, wrap="word")
        scrollable_label.pack(padx=10, pady=10, fill="both", expand=True)

        scrollable_label.insert("0.0", error)
        scrollable_label.configure(state="disabled")  # Make it read-only

        root.protocol("WM_DELETE_WINDOW", self._exit)
        root.update()
        root.after(100, root.geometry, "")
        root.mainloop()

    def _exit(self):
        self._root.destroy()
        sys.exit(1)


def handle_crash(func):
    """Makes the decorated function show an error popup if it crashes."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:  # noqa
            error_msg = traceback.format_exc()
            CrashWindow(error_msg)

    return wrapper

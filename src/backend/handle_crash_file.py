"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import sys
import traceback
import logging
from platformdirs import user_config_dir
from pathlib import Path

from customtkinter import CTk, CTkTextbox, CTkLabel, CTkButton
from tkinter.filedialog import asksaveasfilename
import shutil
import subprocess
import os
from time import sleep


class CrashWindow:
    def __init__(self, error: str):
        root = CTk()
        root.title('Critical Error')
        self._root = root
        super().__init__()
        CTkLabel(root,
                 text='A critical error has occurred.\n'
                      'Please send the log file along with your .gavl file\n'
                      'to the Author at issues.gavl@gmail.com\n'
                 ).grid(row=0, column=0, padx=10, pady=10)
        CTkButton(root, text='Get Log File', command=self._get_log_file).grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=0)
        # Create a read-only textbox that looks like a label
        scrollable_label = CTkTextbox(root, width=1000, height=400, wrap="word")
        scrollable_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

        scrollable_label.insert("0.0", error)
        scrollable_label.configure(state="disabled")  # Make it read-only

        root.protocol("WM_DELETE_WINDOW", self._exit)
        root.update()
        root.update_idletasks()
        root.after_idle(root.geometry, "")
        root.mainloop()

    def _exit(self):
        self._root.destroy()
        sys.exit(0)

    @staticmethod
    def _get_log_file():
        log_file_path = Path(user_config_dir("GAVL")) / "logs.txt"
        new_path = Path(asksaveasfilename(defaultextension='.txt',
                                          filetypes=[('Text File', ['.txt'])],
                                          title='Save Log File',
                                          initialfile='logs.txt'))
        shutil.copy(log_file_path, new_path)


def handle_crash(func):
    """Makes the decorated function show an error popup if it crashes."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:  # noqa
            error_msg = traceback.format_exc()
            logging.critical(error_msg)
            logging.shutdown()
            subprocess.Popen(
                [sys.executable, os.path.abspath(__file__), error_msg],
                start_new_session=True
            )
            sleep(1)
            sys.exit(1)
    return wrapper


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: crash_ui.py <logfile>")
    CrashWindow(sys.argv[1])

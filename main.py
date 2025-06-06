"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


import traceback
from src.app import App
from src.scenes import InitialScene
from src.frontend.crash_window import CrashWindow

try:
    app = App()
    app.set_scene(InitialScene(app))
    app.run()
except Exception as e:
    error_msg = traceback.format_exc()
    CrashWindow(error_msg)

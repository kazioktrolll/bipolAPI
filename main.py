# """
# Copyright (c) 2025 Wojciech Kwiatkowski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# """
#

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


# import customtkinter as ctk
#
#
# root = ctk.CTk()
# ctk.CTkLabel(root, text='Name1').grid(row=0, column=0, padx=10, pady=10)
# ctk.CTkLabel(root, text='Name2').grid(row=1, column=0, padx=10, pady=10)
# ctk.CTkLabel(root, text='Name3').grid(row=2, column=0, padx=10, pady=10)
# ctk.CTkOptionMenu(root, values=['Bind1', 'Bind2', 'Bind3']).grid(row=1, column=1, padx=10, pady=10)
# ctk.CTkOptionMenu(root, values=['Constant']).grid(row=0, column=2, padx=10, pady=10)
# ctk.CTkOptionMenu(root, values=['Constant']).grid(row=1, column=2, padx=10, pady=10)
# ctk.CTkOptionMenu(root, values=['Constant']).grid(row=2, column=2, padx=10, pady=10)
# ctk.CTkEntry(root).grid(row=0, column=3, padx=10, pady=10)
# ctk.CTkEntry(root).grid(row=1, column=3, padx=10, pady=10)
# ctk.CTkEntry(root).grid(row=2, column=3, padx=10, pady=10)
# ctk.CTkButton(root, text='Set').grid(row=0, column=4, padx=10, pady=10)
# ctk.CTkButton(root, text='Set').grid(row=1, column=4, padx=10, pady=10)
# ctk.CTkButton(root, text='Set').grid(row=2, column=4, padx=10, pady=10)
# ctk.CTkButton(root, text='Bind').grid(row=0, column=5, padx=10, pady=10)
# ctk.CTkButton(root, text='Bind', fg_color=ctk.CTkButton(None).cget('hover_color')).grid(row=1, column=5, padx=10, pady=10)
# ctk.CTkButton(root, text='Bind').grid(row=2, column=5, padx=10, pady=10)
# root.mainloop()
#
#
# root2 = ctk.CTk()
# bgc = 'gray20'
# ctk.CTkOptionMenu(root2, values=['Name1'], fg_color=bgc, button_color=bgc).grid(row=0, column=0, padx=10, pady=10)
# ctk.CTkOptionMenu(root2, values=['Name2 -> Bind1']).grid(row=1, column=0, padx=10, pady=10)
# ctk.CTkOptionMenu(root2, values=['Name3'], fg_color=bgc, button_color=bgc).grid(row=2, column=0, padx=10, pady=10)
# ctk.CTkOptionMenu(root2, values=['Constant']).grid(row=0, column=2, padx=10, pady=10)
# ctk.CTkOptionMenu(root2, values=['Constant']).grid(row=1, column=2, padx=10, pady=10)
# ctk.CTkOptionMenu(root2, values=['Constant']).grid(row=2, column=2, padx=10, pady=10)
# ctk.CTkEntry(root2).grid(row=0, column=3, padx=10, pady=10)
# ctk.CTkEntry(root2).grid(row=1, column=3, padx=10, pady=10)
# ctk.CTkEntry(root2).grid(row=2, column=3, padx=10, pady=10)
# ctk.CTkButton(root2, text='Set').grid(row=0, column=4, padx=10, pady=10)
# ctk.CTkButton(root2, text='Set').grid(row=1, column=4, padx=10, pady=10)
# ctk.CTkButton(root2, text='Set').grid(row=2, column=4, padx=10, pady=10)
# root2.mainloop()

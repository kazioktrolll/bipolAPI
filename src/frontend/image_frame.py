"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkFrame, CTkImage, CTkLabel, CTkToplevel
from pathlib import Path
from PIL import Image
from tkinter.filedialog import asksaveasfilename


class ImageFrame(CTkFrame):
    def __init__(self,
                 master: CTkFrame | CTkToplevel,
                 img: Image.Image,
                 size: tuple[int, int] = (800, 800),
                 auto_size_adjust = True):
        """A widget for displaying an image."""
        super().__init__(master)
        self.pil_image = img
        self.img_ar = self.pil_image.size[0] / self.pil_image.size[1]
        self.ctk_image = CTkImage(self.pil_image, size=size)
        self.image_label = CTkLabel(self, image=self.ctk_image, text='')
        self.image_label.pack(fill='both', expand=True)

        if auto_size_adjust:
            self.bind("<Configure>", self.resize_image)

    def resize_image(self, event):
        container_width = event.width
        container_height = event.height

        # Calculate new size preserving aspect ratio
        if container_width / self.img_ar <= container_height:
            new_width = container_width
            new_height = int(container_width / self.img_ar)
        else:
            new_height = container_height
            new_width = int(container_height * self.img_ar)

        # Create a new CTkImage with resized PIL image
        resized_ctk_image = CTkImage(self.pil_image, size=(new_width, new_height))
        self.image_label.configure(image=resized_ctk_image)
        self.image_label.image = resized_ctk_image  # Prevent garbage collection

    def save(self):
        path = Path(asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG File', ['.png'])],
            title='Save Image',
        ))
        self.pil_image.save(path)

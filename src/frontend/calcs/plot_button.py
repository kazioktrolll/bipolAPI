"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from customtkinter import CTkButton, CTkToplevel, CTkImage, CTkLabel
from pathlib import Path
from PIL import Image
from tkinter.filedialog import asksaveasfilename
from abc import ABC, abstractmethod
from src.backend import ImageGetter



class PlotButton(CTkButton, ABC):
    def __init__(self, parent):
        super().__init__(parent, text='Plot Trefftz', command=self.plot)

    @abstractmethod
    def generate_image(self) -> Image.Image:
        pass

    def plot(self):
        PlotWindow(self.generate_image())


class PlotTrefftz(PlotButton):
    def __init__(self, parent, app_wd: str | Path, calc_display):
        super().__init__(parent)
        self._calc_display = calc_display
        self.app_wd = app_wd

    def generate_image(self) -> Image.Image:
        geometry = self.calc_display.geometry
        run_file_data: dict[str, list[float]] = self.calc_display.oip.get_run_file_data()[0]
        case_number: int = self.current_page
        png_path = ImageGetter.get_trefftz(
            geometry, run_file_data, case_number,
            self.calc_display.static_input.height, self.app_wd
        )
        return Image.open(png_path).rotate(-90, expand=True)

    @property
    def calc_display(self):
        from .calc_display import CalcDisplay
        assert isinstance(self._calc_display, CalcDisplay)
        return self._calc_display

    @property
    def current_page(self):
        return self.calc_display.results_display.page


class PlotWindow(CTkToplevel):
    def __init__(self, img: Image.Image):
        super().__init__(None)
        self.title('Image')
        self._image = img
        self.img_ar = self._image.size[0] / self._image.size[1]
        self.image = CTkImage(self._image, size=(800, 800))
        self.image_label = CTkLabel(self, image=self.image, text='')
        self.image_label.pack(fill='both', expand=True)

        self.save_button = CTkButton(self, text='Save', command=self.save)
        self.save_button.place(x=0, y=0)

        self.bind("<Configure>", self.resize_image)
        self.geometry("800x800")

        self.after(50, self.lift,) # noqa
        self.focus_force()

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
        resized_ctk_image = CTkImage(self._image, size=(new_width, new_height))
        self.image_label.configure(image=resized_ctk_image)
        self.image_label.image = resized_ctk_image  # Prevent garbage collection

    def save(self):
        path = Path(asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG File', ['.png'])],
            title='Save Image',
        ))
        self._image.save(path)

"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import re
from pathlib import Path
from subprocess import run, CalledProcessError
from threading import Thread
from time import sleep

from PIL import Image

from .avl_interface import AVLInterface
from ..geo_design import Geometry


def get_gs_path() -> Path:
    base_path = Path(__file__).resolve().parent.parent.parent
    gs_exe = base_path / "ghostscript" / "bin" / "gswin64.exe"
    if not gs_exe.exists():
        raise FileNotFoundError('Cannot find GhostScript executable')
    return gs_exe


class ImageGetter:
    @classmethod
    def get_image(cls, avl_file_path: str | Path, command: str, app_wd: str | Path) -> Path:
        """
        Returns the path to a .png image created by the given command.

        :param avl_file_path: The path to the .avl file.
        :param command: Full command that will create the image, including 'H', return to top level, and 'Q'.
        :param app_wd: App working directory.
        :return: Path to the .png image.
        """
        dump = AVLInterface.execute(command, avl_file_path, app_wd)

        img_dir = Path(app_wd) / 'images'
        if not img_dir.exists(): img_dir.mkdir()

        pattern = re.compile(r"img_(?P<index>\d+)\.png")
        # Extract numbers from matching filenames
        numbers = [
            int(match.group("index"))
            for file in img_dir.iterdir()
            if (match := pattern.match(file.name))
        ]
        next_number = max(numbers, default=0) + 1

        png_path = img_dir / f'img_{next_number}.png'
        ps_path = app_wd / 'plot.ps'
        if not ps_path.exists():
            raise FileNotFoundError('Cannot find plot.ps file')

        cls.ps2png(ps_path, png_path)
        Thread(target=cls.cleanup, args=(ps_path,), daemon=True).start()
        return png_path

    @staticmethod
    def cleanup(ps_path: Path, wait_time: float = 3):
        sleep(wait_time)
        ps_path.unlink()

    @classmethod
    def ps2png(cls, ps_path: str | Path, png_path: str | Path, add_background: bool = True):
        """Converts the given PostScript file to a PNG file."""
        try:
            run([
                get_gs_path(),
                "-dSAFER", "-dBATCH", "-dNOPAUSE",
                f"-sDEVICE={"png16m" if add_background else "pngalpha"}",
                "-r300",
                f"-sOutputFile={png_path}",
                ps_path
            ], check=True)
        except CalledProcessError as e:
            raise RuntimeError(e)

    @classmethod
    def image_from_path(cls, path: Path) -> Image.Image:
        return Image.open(path).rotate(-90, expand=True)

    @classmethod
    def get_trefftz(cls,
                    geometry: Geometry,
                    run_file_data: dict[str, list[float]],
                    case_number: int,
                    height: float,
                    app_wd: str | Path) -> Image.Image:
        """Returns a Trefftz plot of the given conditions.

        :param geometry: The geometry of the aircraft.
        :param run_file_data: Run-file type data.
        :param case_number: The number of the case considered.
        :param height: The altitude of the aircraft.
        :param app_wd: App working directory.
        :return: The Trefftz plot as a PIL Image.
        """
        contents = AVLInterface.create_run_file_contents(run_file_data, height)

        work_dir = Path(app_wd) / 'trefftz'
        if not work_dir.exists(): work_dir.mkdir()
        avl_file_path = work_dir / 'plane.avl'
        run_file_path = work_dir / 'plane.run'

        with open(avl_file_path, 'w') as avl_file: avl_file.write(geometry.string())
        with open(run_file_path, 'w') as run_file: run_file.write(contents)

        command = ('OPER\n'
                   f'{case_number + 1}\n'
                   'X\n'
                   'T\n'
                   'H\n'
                   '\n'
                   '\n'
                   'Q\n')
        png_path = cls.get_image(avl_file_path, command, app_wd)
        return cls.image_from_path(png_path)

    @classmethod
    def get_geometry(cls,
                     geometry: Geometry,
                     app_wd: str | Path) -> Image.Image:
        """Returns an image of the aircraft's geometry as seen by AVL.

        :param geometry: The geometry of the aircraft.
        :param app_wd: App working directory.
        :return: The geometry image as a PIL.Image.Image."""

        work_dir = Path(app_wd) / 'geometry'
        if not work_dir.exists(): work_dir.mkdir()
        avl_file_path = work_dir / 'plane.avl'
        with open(avl_file_path, 'w') as avl_file: avl_file.write(geometry.string())

        command = ('OPER\n'
                   'G\n'
                   'H\n'
                   '\n'
                   '\n'
                   'Q\n')
        png_path = cls.get_image(avl_file_path, command, app_wd)
        return cls.image_from_path(png_path)

    @classmethod
    def get_loading(cls,
                    geometry: Geometry,
                    run_file_data: dict[str, list[float]],
                    case_number: int,
                    height: float,
                    app_wd: str | Path) -> Image.Image:
        """Returns a loading plot of the given conditions.

        :param geometry: The geometry of the aircraft.
        :param run_file_data: Run-file type data.
        :param case_number: The number of the case considered.
        :param height: The altitude of the aircraft.
        :param app_wd: App working directory.
        :return: The Trefftz plot as a PIL Image.
        """
        contents = AVLInterface.create_run_file_contents(run_file_data, height)

        work_dir = Path(app_wd) / 'loading'
        if not work_dir.exists(): work_dir.mkdir()
        avl_file_path = work_dir / 'plane.avl'
        run_file_path = work_dir / 'plane.run'

        with open(avl_file_path, 'w') as avl_file: avl_file.write(geometry.string())
        with open(run_file_path, 'w') as run_file: run_file.write(contents)

        command = ('OPER\n'
                   f'{case_number + 1}\n'
                   'X\n'
                   'G\n'
                   'LO\n'
                   'CH\n'
                   'BO\n'
                   'AX\n'
                   'H\n'
                   '\n'
                   '\n'
                   'Q\n')
        png_path = cls.get_image(avl_file_path, command, app_wd)
        return cls.image_from_path(png_path)

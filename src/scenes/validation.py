"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from .scene import Scene
from ..frontend.validation import ValidationDisplay


class ValidationScene(Scene):
    def build(self) -> None:
        self.app.geometry.distribute_points()
        ValidationDisplay(self).pack(fill='both', expand=True)
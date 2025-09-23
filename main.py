"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from src.app import App
from src.scenes import GeoDesignScene, CalcScene
from src.backend.geo_design import GeometryGenerator
import logging


logging.basicConfig(level=logging.DEBUG)
app = App()
app.set_geometry(GeometryGenerator.default())
app.set_scene(CalcScene(app))
app.run()

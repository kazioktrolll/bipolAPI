from src.app import App
from src.scenes import GeoDesignScene
from src.backend.geo_design import Wing, Geometry, Section
from customtkinter import CTk


app = App()
wing = Wing.simple_tapered(app.geometry, taper_ratio=.7, sweep_angle=15)
app.set_scene(GeoDesignScene(app))
app.run()
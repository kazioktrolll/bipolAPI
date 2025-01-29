from src.app import App
from src.scenes import GeoDesignScene
from src.backend.geo_design import Wing, Geometry
from customtkinter import CTk


app = App()
app.set_scene(GeoDesignScene(app))
geo = Geometry('', 8, 1, 8)
wing = Wing.simple_tapered(geo, taper_ratio=.8, sweep_angle=15)
app.scene.geometry_display.display_wing(wing)
# app.scene.geometry_display.clear()
app.run()
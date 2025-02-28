from src.app import App
from src.scenes import GeoDesignScene

from src.backend.geo_design import GeometryGenerator


app = App()
app.geometry = GeometryGenerator.from_avl(r"C:\Users\kazio\OneDrive\Pulpit\BIPOL\plane.avl")
app.set_scene(GeoDesignScene(app))
app.run()

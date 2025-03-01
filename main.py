from src.app import App
from src.scenes import GeoDesignScene
from src.backend.geo_design import GeometryGenerator


app = App()
app.geometry = GeometryGenerator.default()
app.set_scene(GeoDesignScene(app))
app.run()

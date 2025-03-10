from src.app import App
from src.scenes import InitialScene
from src.backend.geo_design import GeometryGenerator


app = App()
app.geometry = GeometryGenerator.default()
app.set_scene(InitialScene(app))
app.run()

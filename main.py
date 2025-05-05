from src.app import App
from src.scenes import InitialScene
from src.backend.geo_design import GeometryGenerator


app = App()
app.import_from_avl(r"C:\Users\kazio\OneDrive\Pulpit\BIPOL\plane.avl")
app.set_scene(InitialScene(app))
app.scene.goto_geodesign()
app.run()

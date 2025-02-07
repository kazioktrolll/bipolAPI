from src.app import App
from src.scenes import GeoDesignScene


app = App()
app.set_scene(GeoDesignScene(app))
app.geometry.wing.set_mechanization(ailerons=[(3, 3.8, .8)], flaps=[(1, 3, .8)])
app.run()

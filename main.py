from src.app import App
from src.scenes import GeoDesignScene


app = App()
app.set_scene(GeoDesignScene(app))
app.run()
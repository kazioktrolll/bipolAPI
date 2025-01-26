from src.app import App
from src.scenes import InitialScene


app = App()
app.set_scene(InitialScene(app))
app.run()

from Graphics import App, AvlMainScene
from temp import TrialScene


app = App()
app.set_scene(AvlMainScene(app))
app.scene.lift()
app.run()
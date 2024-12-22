from Graphics import App, AvlMainStage
from temp import TrialScene


app = App()
app.set_scene(AvlMainStage(app))
app.scene.lift()
app.run()
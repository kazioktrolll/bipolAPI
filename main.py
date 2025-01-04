from Graphics import App, Avl_handler, SceneAvlInitial, SceneGeneralInitial
from temp import TrialScene


app = App()
app.set_scene(SceneGeneralInitial(app))
app.run()
from Graphics import App, Avl_handler, SceneAvlInitial, SceneGeneralInitial
from temp import TrialScene


app = App()
avl = Avl_handler()
app.active_handler = avl
app.set_scene(SceneGeneralInitial(app))
app.run()
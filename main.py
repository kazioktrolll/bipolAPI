from Graphics import App, Avl_handler
from temp import TrialScene


app = App()
avl = Avl_handler(app)
app.active_handler = avl
avl.current_scene.lift()
app.run()
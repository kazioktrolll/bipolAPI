# from src.app import App
# from src.scenes import GeoDesignScene
#
#
# app = App()
# app.set_scene(GeoDesignScene(app))
# app.run()

from src.backend.geo_design import Airfoil
from pathlib import Path

# af = Airfoil.from_file(Path(r"C:\Users\kazio\Downloads\right.dat"), "right")
af = Airfoil.from_naca("0012")
print(af.string())

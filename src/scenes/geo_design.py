from sys import platform
from .scene import Scene
from ..backend.geo_design import Geometry
from ..frontend import GeometryDisplay, ViewMode, LeftMenu


class GeoDesignScene(Scene):
    def __init__(self, app) -> None:
        self.geometry_display = None
        self.left_menu = None
        super().__init__(app)

    def build(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        geometry_display = GeometryDisplay(self)
        self.geometry_display = geometry_display
        self.to_update.append(geometry_display)
        geometry_display.grid(row=0, column=1, sticky='nsew')
        geometry_display.draw()

        if platform in ("linux",  "linux2"):
            self.bind("<Button-4>", lambda e: geometry_display.zoom())
            self.bind("<Button-5>", lambda e: geometry_display.unzoom())
        else:
            self.bind("<MouseWheel>", geometry_display.scroll_zoom)
        self.bind("<Button-1>", geometry_display.start_drag)
        # self.bind("<Button-1>", lambda e: print("clicked:", e.widget.cget("text")))
        self.bind("<B1-Motion>", geometry_display.drag)
        self.bind("<ButtonRelease-1>", geometry_display.stop_drag)
        self.bind("<w>", lambda e: geometry_display.change_view(ViewMode.TOP))
        self.bind("<s>", lambda e: geometry_display.change_view(ViewMode.FRONT))
        self.bind("<d>", lambda e: geometry_display.change_view(ViewMode.RIGHT))
        self.bind("<a>", lambda e: geometry_display.change_view(ViewMode.ISO))

        lm = LeftMenu(self, self.geometry_display.update)
        lm.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.left_menu = lm

    @property
    def geometry(self) -> Geometry:
        return self.app.geometry

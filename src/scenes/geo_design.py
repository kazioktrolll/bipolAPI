from .scene import Scene
from ..frontend import GeometryDisplay, LeftMenuWing, LeftMenu


class GeoDesignScene(Scene):
    def build(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        geometry_display = GeometryDisplay(self, self.app.geometry)
        self.to_update.append(geometry_display)
        geometry_display.grid(row=0, column=1, sticky='nsew')
        geometry_display.draw()

        LeftMenu(self, self.app.geometry, self.geometry_display.update).grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

    @property
    def geometry_display(self):
        return self.children['!geometrydisplay']

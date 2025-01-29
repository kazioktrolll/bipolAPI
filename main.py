from customtkinter import CTk
from src.frontend import GeometryDisplay
from src.backend.geo_design import Geometry, Wing, Section


app = CTk()
app.rowconfigure(0, weight=1)
app.columnconfigure(0, weight=1)
geo_dis = GeometryDisplay(app, (1000, 400))
geo_dis.grid(row=0, column=0, sticky='nsew')

geo = Geometry('', 8, 1, 8)
wing = Wing.simple_tapered(geo, (0,0,0), 0, [], .5, 15)
wing.add_section_gentle([1, 2, 3])
#TODO: fix /\

geo_dis.after(10, geo_dis.display_wing(wing))
app.after(0, lambda: app.state('zoomed'))
app.mainloop()
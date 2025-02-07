from customtkinter import CTkFrame, CTkLabel, CTkButton


class ListPreset(CTkFrame):
    def __init__(self, parent, category_name: str) -> None:
        CTkFrame.__init__(self, parent)
        self.columnconfigure(0, weight=1)

        self.header_frame = CTkFrame(self, fg_color=self.cget('fg_color'))
        self.header_frame.grid(column=0, row=0, sticky="new")
        self.header_frame.columnconfigure(1, weight=1)
        CTkLabel(self.header_frame, text=category_name).grid(column=0, row=0, sticky="w", padx=5, pady=5)
        CTkButton(self.header_frame, text='+', fg_color='green', hover_color='dark green', width=25, height=25, command=self.add_position
                  ).grid(column=1, row=0, sticky="e", padx=5, pady=5)

        self.body_frame = CTkFrame(self, height=0)
        self.body_frame.grid(column=0, row=1, sticky="sew", padx=5, pady=5)
        self.body_frame.columnconfigure(0, weight=1)

    def add_position(self):
        position = CTkFrame(self.body_frame, fg_color=self.body_frame.cget('fg_color'))
        position.grid(column=0, row=len(self.body_frame.children)-1, sticky="nsew")
        position.columnconfigure(0, weight=1)

        CTkButton(position, text='E', width=25, height=25
                  ).grid(column=1, row=0, sticky="e", padx=5, pady=5)
        CTkButton(position, text='-', fg_color='red3', hover_color='red4', width=25, height=25, command=position.destroy
                  ).grid(column=2, row=0, sticky="e", padx=5, pady=5)

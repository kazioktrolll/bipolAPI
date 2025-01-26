from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkEntry


class Scene(CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.button = CTkButton(master, text="Load File", command=self.open_file)
        self.button.grid(column=0, row=0)
        self.path = ""

    def open_file(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select File",
            initialdir=r"C:\Users\kazio\OneDrive\Pulpit\BIPOL",
            filetypes=(("AVL Files", "*.avl"),)
        )
        self.path = path
        self.goto_oper()

    def goto_oper(self):
        self.button.destroy()

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left_frame = CTkFrame(self)
        left_frame.grid(column=0, row=0, sticky='nsew')
        left_frame.columnconfigure(0, weight=1)

        self.alfa = ParameterField(left_frame, "Alfa")
        self.alfa.grid(column=0, row=0)
        self.beta = ParameterField(left_frame, "Beta")
        self.beta.grid(column=0, row=1)
        self.roll = ParameterField(left_frame, "Roll")
        self.roll.grid(column=0, row=2)
        self.pitch = ParameterField(left_frame, "Pitch")
        self.pitch.grid(column=0, row=3)
        self.yaw = ParameterField(left_frame, "Yaw")
        self.yaw.grid(column=0, row=4)
        self.flap = ParameterField(left_frame, "Flap")
        self.flap.grid(column=0, row=5)

        self.fake_output = FakeOutput(self)
        self.fake_output.grid(column=1, row=0, sticky='nsew')

        CTkButton(left_frame, text="Run",
                  command=self.run_avl
                  ).grid(column=0, row=6, sticky='nsew')

    def get_values(self):
        return self.alfa.value, self.beta.value, self.roll.value, self.pitch.value, self.yaw.value, self.flap.value

    def run_avl(self):
        input_values = self.get_values()
        keys = ['alfa', 'beta', 'roll', 'pitch', 'yaw', 'flap']
        val_dict = {key: value for key, value in zip(keys, input_values)}
        text = get_avl_data(r"C:\Users\kazio\OneDrive\Pulpit\BIPOL\plane.avl", **val_dict)
        output_dict = format_avl_response(text)
        dict_to_string = '\n'.join([f'{key} = {value}' for key, value in output_dict.items()])
        self.fake_output.configure(text=dict_to_string)


class ParameterField(CTkFrame):
    def __init__(self, master, name):
        super().__init__(master)
        self.name = name
        self.value = 0

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

        CTkLabel(self, text=name).grid(column=0, row=0, sticky="w")
        self.value_label = CTkLabel(self, text=str(self.value))
        self.value_label.grid(column=1, row=0, sticky="w", padx=10)
        self.entry = CTkEntry(self)
        self.entry.grid(column=2, row=0, sticky="ew")
        CTkButton(self, text="Set", width=30, command=self.set).grid(column=3, row=0, sticky="e")

    def set(self):
        value = self.entry.get()
        self.value = float(value)
        self.entry.delete(0, "end")
        self.value_label.configure(text=value)

    def grid(self, **kwargs):
        kwargs['padx'] = 10
        kwargs['pady'] = 10
        super().grid(**kwargs)


class FakeOutput(CTkLabel):
    def __init__(self, master):
        super().__init__(master)
        self.configure(text=self.get_text(0,0,0,0,0,0))

    def get_text(self, alfa, beta, roll, pitch, yaw, flaps):
        text = ("Operation of run case 1/1:   -unnamed-\n"
                 "==========================================================\n"
                 "\n"
                 "variable          constraint\n"
                 "------------      ------------------------\n"
                 f"A lpha        ->  alpha       =   {alfa}\n"
                f"B eta         ->  beta        =   {beta}\n"
                f"R oll  rate   ->  pb/2V       =   {roll}\n"
                f"P itch rate   ->  qc/2V       =   {pitch}\n"
                f"Y aw   rate   ->  rb/2V       =   {yaw}\n"
                f"D1  flap      ->  flap        =   {flaps}\n"
                "------------      ------------------------\n")
        return text

    def set_text(self, alfa, beta, roll, pitch, yaw, flaps):
        self.configure(text=self.get_text(alfa, beta, roll, pitch, yaw, flaps))

def get_avl_data(file_path, **values) -> str:
    from subprocess import Popen, PIPE
    command = (f'LOAD {file_path}\n'
               f'OPER\n'
               f'a a {values["alfa"]}\n'
               f'b b {values["beta"]}\n'
               f'r r {values['roll']}\n'
               f'p p {values['pitch']}\n'
               f'y y {values["yaw"]}\n'
               f'd1 d1 {values["flap"]}\n'
               f'x\n')
    avl = Popen(r"C:\Users\kazio\OneDrive\Pulpit\BIPOL\avl.exe",
                stdout=PIPE, stdin=PIPE, stderr=PIPE)
    text = avl.communicate(command.encode())[0].decode()
    avl.kill()
    return text

def format_avl_response(response) -> dict[str, float]:
    text = response.split("c>")[-2]
    text = text.split("-unnamed-")[1]
    text = text.split("---")[0]
    text = text.replace("| Trefftz", "")
    text = text.replace("| Plane", "")
    text_split = text.split(" ")
    text_split = [fragment.replace('\r\n', '') for fragment in text_split]
    text_split = [fragment.replace('=', '') for fragment in text_split]
    text_split = [fragment for fragment in text_split if fragment]
    return_dict = {}
    for i in range(len(text_split)//2):
        key = text_split[i*2]
        value = float(text_split[i*2+1])
        return_dict[key] = value

    return return_dict

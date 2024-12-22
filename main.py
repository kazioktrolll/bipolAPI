import threading
from handlers import avl, xfoil


class BaseAPIApp:
    def __init__(self, root):
        self.root = root
        root.main = self

        # Start the base program
        self.process = avl()

        self.output_thread = threading.Thread(target=self.read_output, daemon=True)
        self.output_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def send_command(self, command):
        """Send a command to the base process."""
        if self.process.poll() is None:  # Check if the process is still running
            self.process.stdin.write(command)
            self.process.stdin.flush()
            self.root.scene.output_area.insert(command)
        else:
            self.root.scene.output_area.insert("Base process has terminated.\n")
        self.root.scene.command_input_field.delete(0, len(self.root.scene.command_input_field.get()))

    def read_output(self):
        """Continuously read output from the base process."""
        while True:
            char = self.process.stdout.read(1)
            self.root.scene.output_area.insert(char)
            self.root.scene.output_area.scroll_down()

    def on_close(self):
        """Handle the close event by terminating the base process."""
        self.process.terminate()
        self.root.destroy()


# Create the base API interface
if __name__ == "__main__":
    from Graphics import App
    from temp import trial_scene
    tk_root = App()
    tk_root.set_scene(trial_scene(tk_root))
    app = BaseAPIApp(tk_root)
    tk_root.run()
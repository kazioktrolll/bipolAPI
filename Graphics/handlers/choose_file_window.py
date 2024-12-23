import customtkinter as ctk
from tkinter import filedialog

def open_file_path_dialog(filetypes: list[tuple[str, str]]|None=None) -> str|None:
    """
    Opens a file path selector window and returns the selected file path.

    :param filetypes: A list of tuples containing file extensions and their descriptions
                      in format ("Description", "*.ext1;*.ext2").
                      Defaults to all files.
    :return: The selected file path as a string in the format "C:/dir1/dir2/file.ext",
             or 'None' if no file is selected.
    """
    filetypes = filetypes or [("All Files", "*.*")]
    modal_window = ctk.CTkToplevel(None)
    modal_window.withdraw()
    modal_window.grab_set()

    file_path = filedialog.askopenfilename(title="Select a File", parent=modal_window, filetypes=filetypes)

    modal_window.grab_release()
    modal_window.destroy()
    return file_path if file_path else None


# Example of using the FilePathSelector class
if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Main Window")
    root.geometry("500x300")

    def open_selector():
        print(open_file_path_dialog())

    open_selector_button = ctk.CTkButton(root, text="Open File Path Selector", command=open_selector)
    open_selector_button.pack(pady=20)

    root.mainloop()

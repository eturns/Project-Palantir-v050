from tkinter import Tk, filedialog

def select_mesbg_json_file() -> str | None:
    """
    Opens a native file-selection dialog for choosing an
    MESBG List Builder JSON export.
    """

    root = Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select MESBG List Builder JSON file",
        filetypes=[
            (
                "JSON files",
                "*.json",
            ),
            (
                "All files",
                "*.*",
            ),
        ],
    )

    root.destroy()

    if not file_path:
        return None

    return file_path
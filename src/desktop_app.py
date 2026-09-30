from tkinter import Button, Label, Tk
from pathlib import Path
from file_selection import select_mesbg_json_file
from desktop_analysis_adapter import run_analysis

def select_and_run_analysis(
    selected_file_label,
    status_label,
) -> None:
    file_path = select_mesbg_json_file()

    if file_path is None:
        return

    selected_file_label.config(
        text=f"Selected: {Path(file_path).name}"
    )

    result = run_analysis(file_path)

    if result is None:
        status_label.config(
            text="Unable to analyse selected file."
        )
        return

    status_label.config(
        text="Analysis complete."
    )

def launch_desktop_app() -> None:
    root = Tk()
    root.title("Project Palantír")

    selected_file_label = Label(
        root,
        text="No file selected",
    )
    selected_file_label.pack()

    status_label = Label(
        root,
        text="",
    )
    status_label.pack()

    select_button = Button(
        root,
        text="Select Army JSON",
        command=lambda: select_and_run_analysis(
            selected_file_label,
            status_label,
        ),
    )
    select_button.pack()

    root.mainloop()

def main() -> None:
    launch_desktop_app()


if __name__ == "__main__":
    main()
    
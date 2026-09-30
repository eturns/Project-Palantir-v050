from main import run_analysis_workflow


def run_analysis(file_path: str) -> dict | None:
    """
    Run the existing Palantír analysis workflow.

    Provides a simple entry point for the desktop
    interface without duplicating analysis logic.
    """
    return run_analysis_workflow(
        file_path,
        print_report=False,
    )

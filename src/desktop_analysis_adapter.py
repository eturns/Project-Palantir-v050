from main import run_analysis_workflow
from desktop_analysis_view_model import (
    build_desktop_analysis_view_model,
)


def run_analysis(file_path: str) -> dict | None:
    """
    Run the existing Palantír analysis workflow and
    convert the result into desktop presentation data.

    The desktop UI consumes presentation data only;
    analysis logic remains in the existing engine.
    """
    result = run_analysis_workflow(
        file_path,
        print_report=False,
    )

    if result is None:
        return None

    return build_desktop_analysis_view_model(
        result,
    )

"""Project Palantír — web engine adapter.

DEV-079-A3-3
Author: Edward Turns (Project Lead)

Reuse the existing Palantír analysis pathway.
No independent combat, scenario or calibration calculations.
"""

import sys
from pathlib import Path

from web.backend.result_mapper import build_web_analysis_result


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"


def analyse_army_for_web(file_path: str | Path) -> dict:
    """Analyse an existing army file through the established engine."""

    if str(SOURCE_DIRECTORY) not in sys.path:
        sys.path.insert(0, str(SOURCE_DIRECTORY))

    from desktop_analysis_adapter import run_analysis

    army_path = Path(file_path).resolve()

    if not army_path.is_file():
        raise FileNotFoundError("Army JSON file not found")

    # Existing analysis code loads CSVs using relative paths.
    # Require the expected working directory for this first
    # local integration stage rather than silently changing it.
    if Path.cwd().resolve() != PROJECT_ROOT.resolve():
        raise RuntimeError(
            "Run Palantír from the project root directory"
        )

    view = run_analysis(str(army_path))

    if view is None:
        raise ValueError("The army could not be analysed")

    return build_web_analysis_result(view)

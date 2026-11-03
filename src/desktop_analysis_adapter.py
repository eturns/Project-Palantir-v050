"""Desktop presentation bridge; scenario and optimiser outputs are untouched."""
from main import run_analysis_workflow
from desktop_analysis_view_model import build_desktop_analysis_view_model
from provisional_desktop_view import build_provisional_desktop_view
from provisional_mechanical_measurements import collect_provisional_mechanical_evidence
from army import Army
from provisional_magic_web_evidence import (
    build_provisional_magic_web_evidence,
)

def run_analysis(file_path: str) -> dict | None:
    result = run_analysis_workflow(file_path, print_report=False)
    if result is None:
        return None
    view = build_desktop_analysis_view_model(result)
    army = result.get('army') if isinstance(result, dict) else None
    # Some tests and external consumers use lightweight stubs. Those retain
    # an unevaluated display instead of being mistaken for a real army.
    mechanical = collect_provisional_mechanical_evidence(army) if isinstance(army, Army) else None
    view['provisional_capabilities'] = build_provisional_desktop_view(
        view.get('defence_presentation'),
        qualified_measurements=(mechanical.values if mechanical else None),
        evidence_statuses=(mechanical.statuses if mechanical else None),
    )
    if mechanical:
        view['provisional_evidence_reasons'] = dict(
            mechanical.reasons
        )

    # DEV-080-F5A: Additional display-only Magic
    # evidence. Existing calibrated metrics,
    # scenario results and ratings are unchanged.
    #
    # Lightweight test stubs without a real
    # imported army retain their existing behaviour.
    if isinstance(army, Army) and result.get("army_list") is not None:
        view["provisional_magic"] = (
            build_provisional_magic_web_evidence(
                result
            )
        )

    return view

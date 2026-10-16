"""Desktop analysis view data; legacy ratings and scenarios remain unchanged.

I2-I-E1-B adds two uncalibrated mechanical Defence readings, separately from
legacy metric assessments. It does not replace the old Defence rating yet.
"""

from army import Army
from defence_presentation_contract import build_defence_presentation


def _display_name(value: str) -> str:
    return value.replace("_", " ").title()


def _build_assessment_view(assessment) -> dict:
    return {
        "metric": _display_name(assessment.metric),
        "rating": assessment.rating,
        "value": assessment.value,
    }


def _build_scenario_demand_view(demand) -> dict:
    return {
        "dimension": _display_name(demand.dimension.value),
        "capability": demand.capability,
        "intensity": demand.intensity,
    }


def _build_scenario_view(scenario) -> dict:
    return {
        "scenario_id": scenario.scenario_id,
        "name": scenario.scenario_name,
        "pool": scenario.pool.value,
        "score": scenario.score,
        "demands": tuple(
            _build_scenario_demand_view(demand)
            for demand in scenario.demands
        ),
    }


def _build_evidence_view(evidence) -> dict:
    return {
        "mechanic": _display_name(evidence.mechanic),
        "status": evidence.status.value.upper(),
        "reason": evidence.reason,
        "provenance": evidence.provenance,
    }


def _entry_name(entry) -> str:
    if entry.siege_engine_profile is not None:
        return entry.siege_engine_profile.name
    return entry.profile.name


def _build_key_models(army) -> tuple[dict, ...]:
    entries = []
    for position, entry in enumerate(army.entries):
        entries.append({
            "position": position,
            "name": _entry_name(entry),
            "quantity": entry.quantity,
            "points": entry.total_points(),
        })
    entries.sort(key=lambda item: (-item["points"], item["position"]))
    return tuple({
        "name": item["name"],
        "quantity": item["quantity"],
        "points": item["points"],
    } for item in entries[:6])


def _build_defence_measure_view(measure) -> dict:
    return {
        "key": measure.key,
        "label": measure.label,
        "value": measure.value,
        "unit": measure.unit,
        "explanation": measure.explanation,
        "calibrated": measure.calibrated,
    }


def _build_defence_presentation_view(army) -> dict | None:
    """Only actual Army instances can be mechanically analysed.

    Existing tests and non-Army callers retain their legacy view output.
    Calculation errors for real Armies propagate rather than masquerading as
    a zero or a successful measurement.
    """
    if not isinstance(army, Army):
        return None
    presentation = build_defence_presentation(army)
    return {
        "army_survival_density": _build_defence_measure_view(
            presentation.army_survival_density
        ),
        "per_model_resilience": _build_defence_measure_view(
            presentation.per_model_resilience
        ),
        "engagements": presentation.engagements,
        "benchmark": {
            "fight": presentation.benchmark.fight,
            "strength": presentation.benchmark.strength,
            "defence": presentation.benchmark.defence,
            "attacks": presentation.benchmark.attacks,
            "wounds": presentation.benchmark.wounds,
        },
        "production_score_changed": presentation.production_score_changed,
    }


def build_desktop_analysis_view_model(result: dict) -> dict:
    definition = result["definition"]
    army = result["army"]
    analysis = result["analysis"]
    validation_errors = tuple(analysis["validation_errors"])
    battlefield = analysis["battlefield_assessments"]

    model_count_fn = getattr(army, "model_count", None)
    total_might_fn = getattr(army, "total_might", None)
    total_will_fn = getattr(army, "total_will", None)
    total_fate_fn = getattr(army, "total_fate", None)

    return {
        "army_name": definition.name,
        "total_points": army.total_points(),
        "points_limit": definition.points_limit,
        "model_count": model_count_fn() if callable(model_count_fn) else None,
        "might": total_might_fn() if callable(total_might_fn) else None,
        "will": total_will_fn() if callable(total_will_fn) else None,
        "fate": total_fate_fn() if callable(total_fate_fn) else None,
        "key_models": _build_key_models(army) if hasattr(army, "entries") else (),
        "is_legal": not validation_errors,
        "legality_issues": validation_errors,
        "metrics": tuple(_build_assessment_view(a) for a in analysis.get("metric_assessments", ())),
        "strengths": tuple(_build_assessment_view(a) for a in battlefield.strengths),
        "weaknesses": tuple(_build_assessment_view(a) for a in battlefield.weaknesses),
        "scenarios": tuple(_build_scenario_view(s) for s in (result.get("scenario_analysis_results") or ())),
        "evidence": tuple(_build_evidence_view(e) for e in result.get("evidence_records", ())),
        "defence_presentation": _build_defence_presentation_view(army),
    }

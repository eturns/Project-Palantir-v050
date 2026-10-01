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
        entries.append(
            {
                "position": position,
                "name": _entry_name(entry),
                "quantity": entry.quantity,
                "points": entry.total_points(),
            }
        )

    entries.sort(
        key=lambda item: (
            -item["points"],
            item["position"],
        )
    )

    return tuple(
        {
            "name": item["name"],
            "quantity": item["quantity"],
            "points": item["points"],
        }
        for item in entries[:6]
    )


def build_desktop_analysis_view_model(
    result: dict,
) -> dict:
    definition = result["definition"]
    army = result["army"]
    analysis = result["analysis"]

    validation_errors = tuple(
        analysis["validation_errors"]
    )

    battlefield = analysis[
        "battlefield_assessments"
    ]

    model_count_fn = getattr(
        army,
        "model_count",
        None,
    )
    total_might_fn = getattr(
        army,
        "total_might",
        None,
    )
    total_will_fn = getattr(
        army,
        "total_will",
        None,
    )
    total_fate_fn = getattr(
        army,
        "total_fate",
        None,
    )

    return {
        "army_name": definition.name,
        "total_points": army.total_points(),
        "points_limit": definition.points_limit,
        "model_count": (
            model_count_fn()
            if callable(model_count_fn)
            else None
        ),
        "might": (
            total_might_fn()
            if callable(total_might_fn)
            else None
        ),
        "will": (
            total_will_fn()
            if callable(total_will_fn)
            else None
        ),
        "fate": (
            total_fate_fn()
            if callable(total_fate_fn)
            else None
        ),
        "key_models": (
            _build_key_models(army)
            if hasattr(army, "entries")
            else ()
        ),
        "is_legal": not validation_errors,
        "legality_issues": validation_errors,
        "metrics": tuple(
            _build_assessment_view(assessment)
            for assessment in analysis.get(
                "metric_assessments",
                (),
            )
        ),
        "strengths": tuple(
            _build_assessment_view(assessment)
            for assessment in battlefield.strengths
        ),
        "weaknesses": tuple(
            _build_assessment_view(assessment)
            for assessment in battlefield.weaknesses
        ),
        "scenarios": tuple(
            _build_scenario_view(scenario)
            for scenario in (
                result.get(
                    "scenario_analysis_results"
                )
                or ()
            )
        ),
        "evidence": tuple(
            _build_evidence_view(evidence)
            for evidence in result.get(
                "evidence_records",
                (),
            )
        ),
    }

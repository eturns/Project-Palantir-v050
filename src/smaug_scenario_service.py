"""DEV-077-SMAUG-D6C: production bridge for opt-in scenario evidence.

Edward Turns (Project Lead). No scenario-fit or calibration mutation.
"""
from __future__ import annotations
from dataclasses import dataclass
from army import Army
from smaug_scenario_evidence import build_smaug_scenario_evidence

_ALLOWED = frozenset({
    "distance_to_objective_inches", "objective_range_inches", "moving",
    "charge_targets", "gold_marker_state", "game_ended",
    "smaug_points", "opponent_points",
})


def build_smaug_scenario_service_evidence(
    army: Army, *, scenario_context: dict | None = None,
):
    """Build evidence for the actual fielded Smaug, not a synthetic identity.

    An absent context deliberately yields conditional evidence. An explicit
    context must be a dictionary of approved D6B inputs. Never supply model
    IDs or rule IDs through the context: they come from the loaded army.
    """
    if not isinstance(army, Army):
        raise TypeError("Smaug scenario integration requires a real Army")
    if scenario_context is not None:
        if not isinstance(scenario_context, dict):
            raise TypeError("scenario_context must be a dict or None")
        unknown = scenario_context.keys() - _ALLOWED
        if unknown:
            raise ValueError(f"Unknown Smaug scenario inputs: {sorted(unknown)}")
    models = tuple(model for model in army.fielded_models()
                   if model.counts_as_model and model.profile_id == "SMAUG")
    if not models:
        if scenario_context is not None:
            raise ValueError("Smaug scenario context provided to non-Smaug army")
        return None
    if len(models) != 1:
        raise ValueError("Expected exactly one fielded Smaug")
    model = models[0]
    rules = frozenset(assignment.rule.id for assignment in
                      model.configured_profile.effective_special_rules)
    return build_smaug_scenario_evidence(
        smaug_model_id=model.id,
        rule_ids=rules,
        **(scenario_context if scenario_context is not None else {}),
    )

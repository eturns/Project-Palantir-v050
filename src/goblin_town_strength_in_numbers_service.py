"""DEV-078-GT-C2: imported Goblin-town Strength in Numbers evidence.
Author: Edward Turns (Project Lead).
Explicit Broken/charge context; diagnostic-only and no score changes.
"""
from dataclasses import dataclass
from army import Army
from goblin_town_strength_in_numbers import (
    RULE_ID, StrengthInNumbersContext, assess_strength_in_numbers,
)
from courage_test import CourageTestContext


@dataclass(frozen=True)
class StrengthInNumbersArmyRequest:
    army_broken: bool
    # Each pair is (fielded model ID, whether its test charges a Terror-causing enemy).
    terror_charge_tests_by_model_id: tuple[tuple[str, bool], ...]
    base_courage_context: CourageTestContext = CourageTestContext()


@dataclass(frozen=True)
class StrengthInNumbersModelEvidence:
    model_id: str
    profile_id: str
    result: object


@dataclass(frozen=True)
class StrengthInNumbersArmyEvidence:
    model_tests: tuple[StrengthInNumbersModelEvidence, ...]
    status: str = "explicit_broken_state_and_terror_charge_tests_diagnostic_only"
    dashboard_score: None = None
    scenario_score: None = None


def build_strength_in_numbers_army_evidence(
    army: Army, army_list, *, request: StrengthInNumbersArmyRequest,
) -> StrengthInNumbersArmyEvidence:
    if not isinstance(army, Army):
        raise TypeError("Real Army required")
    if getattr(army_list, "id", None) != "GOBLIN_TOWN":
        raise ValueError("Goblin-town army required")
    if not isinstance(request, StrengthInNumbersArmyRequest):
        raise TypeError("StrengthInNumbersArmyRequest required")
    if type(request.army_broken) is not bool:
        raise TypeError("Army Broken state must be bool")
    if not isinstance(request.base_courage_context, CourageTestContext):
        raise TypeError("CourageTestContext required")
    rules = getattr(army_list, "army_rules", None)
    if not isinstance(rules, (list, tuple)):
        raise TypeError("Registered army rules required")
    rule_ids = tuple(getattr(rule, "id", None) for rule in rules)
    if RULE_ID not in rule_ids:
        raise ValueError("Strength in Numbers is not registered")
    if not isinstance(request.terror_charge_tests_by_model_id, tuple):
        raise TypeError("Terror charge evidence must be tuple")
    models = tuple(army.fielded_models())
    by_id = {m.id: m for m in models}
    if len(models) != len(by_id):
        raise ValueError("Duplicate fielded model IDs")
    seen = set()
    evidence = []
    for pair in request.terror_charge_tests_by_model_id:
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise TypeError("Expected (model ID, terror-charge bool)")
        model_id, is_terror_charge = pair
        if type(is_terror_charge) is not bool:
            raise TypeError("Terror-charge evidence must be bool")
        if model_id in seen:
            raise ValueError("Duplicate model ID in Terror-charge evidence")
        seen.add(model_id)
        model = by_id.get(model_id)
        if model is None or model.configured_profile is None:
            raise ValueError("Test model is not fielded")
        result = assess_strength_in_numbers(
            model.configured_profile,
            StrengthInNumbersContext(
                army_list_id=army_list.id,
                active_army_rule_ids=rule_ids,
                army_broken=request.army_broken,
                friendly_model=True,  # Verified against the fielded friendly Army above.
                is_terror_charge_test=is_terror_charge,
                base_courage_context=request.base_courage_context,
            ),
        )
        evidence.append(StrengthInNumbersModelEvidence(
            model_id=model_id, profile_id=model.profile_id, result=result,
        ))
    return StrengthInNumbersArmyEvidence(tuple(evidence))

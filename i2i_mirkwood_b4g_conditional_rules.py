"""DEV-077S-I2-I-C3-D7-B4-G: read-only Mirkwood rule-applicability review.

These are evidence annotations, not an army-list special-rule runtime.
No production modifiers are granted or altered.
"""
from dataclasses import asdict, dataclass
import json


@dataclass(frozen=True)
class ConditionalRuleReview:
    rule_id: str
    profile_id: str
    registered_on_profile: bool
    active_in_rangers_of_mirkwood: bool
    runtime_implementation_scope: str
    explanation: str


REVIEWS = (
    ConditionalRuleReview(
        rule_id="VENGEFUL_FURY",
        profile_id="MW_TAURIEL",
        registered_on_profile=True,
        active_in_rangers_of_mirkwood=False,
        runtime_implementation_scope="deferred_to_army_rule_applicability",
        explanation=(
            "Tauriel's profile rule requires Kili in the army and his casualty. "
            "The 2024 Rangers of Mirkwood army-list special rules explicitly state "
            "that Vengeful Fury does not apply in this army list."
        ),
    ),
    ConditionalRuleReview(
        rule_id="LEADER_PALACE_GUARD",
        profile_id="MW_LEGOLAS",
        registered_on_profile=True,
        active_in_rangers_of_mirkwood=False,
        runtime_implementation_scope="no_palace_guard_targets_in_reference_roster",
        explanation=(
            "Registered as a Legolas profile rule. This 700-point reference "
            "roster has no Palace Guard recipients. No numerical command "
            "bonus is inferred."
        ),
    ),
)


def review_reference_army() -> dict:
    return {
        "development": "DEV-077S-I2-I-C3-D7-B4-G",
        "army_list": "RANGERS_OF_MIRKWOOD",
        "profile_rule_registry_preserved": True,
        "new_army_rule_runtime": False,
        "new_production_scoring": False,
        "reference_condition_bonuses": {
            "vengeful_fury": 0,
            "leader_palace_guard": 0,
        },
        "rules": [asdict(item) for item in REVIEWS],
    }


if __name__ == "__main__":
    print(json.dumps(review_reference_army(), indent=2))

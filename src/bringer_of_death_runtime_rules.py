from bringer_of_death_state import (
    BringerOfDeathState,
)
from runtime_special_rule_assignment import (
    RuntimeSpecialRuleAssignment,
)


TERROR_RULE_ID = "TERROR"
HARBINGER_OF_EVIL_RULE_ID = "HARBINGER_OF_EVIL"
MIGHTY_HERO_RULE_ID = "MIGHTY_HERO"


def get_bringer_of_death_runtime_rule_ids(
    state: BringerOfDeathState,
) -> frozenset[str]:
    return frozenset(
        assignment.rule_id
        for assignment
        in get_bringer_of_death_runtime_rule_assignments(
            state
        )
    )

def get_bringer_of_death_runtime_rule_assignments(
    state: BringerOfDeathState,
) -> tuple[RuntimeSpecialRuleAssignment, ...]:
    assignments: list[
        RuntimeSpecialRuleAssignment
    ] = []

    if state.gains_terror:
        assignments.append(
            RuntimeSpecialRuleAssignment(
                rule_id=TERROR_RULE_ID,
            )
        )

    if state.gains_harbinger_of_evil:
        assignments.append(
            RuntimeSpecialRuleAssignment(
                rule_id=HARBINGER_OF_EVIL_RULE_ID,
                parameter=12,
            )
        )

    if state.gains_mighty_hero:
        assignments.append(
            RuntimeSpecialRuleAssignment(
                rule_id=MIGHTY_HERO_RULE_ID,
            )
        )

    return tuple(assignments)
from configured_profile import ConfiguredProfile
from torturer_runtime_rules import (
    get_torturer_runtime_rule_ids,
)
from torturer_state import TorturerState
from shattered_spirit_state import (
    ShatteredSpiritState,
)
from bringer_of_death_runtime_rules import (
    get_bringer_of_death_runtime_rule_ids,
    get_bringer_of_death_runtime_rule_assignments
)
from bringer_of_death_state import (
    BringerOfDeathState,
)
from runtime_special_rule_assignment import (
    RuntimeSpecialRuleAssignment,
)

def get_runtime_granted_rule_ids(
    existing_rule_ids: frozenset[str],
    *,
    torturer_state: TorturerState | None = None,
    shattered_spirit_state: ShatteredSpiritState | None = None,
    bringer_of_death_state: BringerOfDeathState | None = None,
) -> frozenset[str]:
    return frozenset(
        assignment.rule_id
        for assignment
        in get_runtime_granted_rule_assignments(
            existing_rule_ids,
            torturer_state=torturer_state,
            shattered_spirit_state=shattered_spirit_state,
            bringer_of_death_state=bringer_of_death_state,
        )
    )

def get_effective_runtime_rule_ids(
    configured_profile: ConfiguredProfile,
    *,
    torturer_state: TorturerState | None = None,
    shattered_spirit_state: ShatteredSpiritState | None = None,
    bringer_of_death_state: BringerOfDeathState | None = None,
) -> frozenset[str]:
    """
    Backwards-compatible helper returning configured static
    rules plus runtime-granted rules.

    New production consumers should prefer
    get_effective_special_rule_ids().
    """

    static_rule_ids = frozenset(
        assignment.rule.id
        for assignment
        in configured_profile.effective_special_rules
    )

    return frozenset(
        static_rule_ids
        | get_runtime_granted_rule_ids(
            static_rule_ids,
            torturer_state=torturer_state,
            shattered_spirit_state=shattered_spirit_state,
            bringer_of_death_state=bringer_of_death_state,
        )
    )

def get_runtime_granted_rule_assignments(
    existing_rule_ids: frozenset[str],
    *,
    torturer_state: TorturerState | None = None,
    shattered_spirit_state: ShatteredSpiritState | None = None,
    bringer_of_death_state: BringerOfDeathState | None = None,
) -> tuple[RuntimeSpecialRuleAssignment, ...]:
    """
    Returns runtime-granted special rules while preserving
    optional rule parameters.

    Existing ID-only consumers can continue to use
    get_runtime_granted_rule_ids().
    """

    assignments: list[
        RuntimeSpecialRuleAssignment
    ] = []

    if (
        torturer_state is not None
        and "TORTURER" in existing_rule_ids
    ):
        assignments.extend(
            RuntimeSpecialRuleAssignment(
                rule_id=rule_id,
            )
            for rule_id in sorted(
                get_torturer_runtime_rule_ids(
                    torturer_state
                )
            )
        )

    if (
        shattered_spirit_state is not None
        and shattered_spirit_state.is_empowered
        and "SHATTERED_SPIRIT" in existing_rule_ids
    ):
        assignments.append(
            RuntimeSpecialRuleAssignment(
                rule_id="FEARLESS",
            )
        )

    if (
        bringer_of_death_state is not None
        and "BRINGER_OF_DEATH"
        in existing_rule_ids
    ):
        assignments.extend(
            get_bringer_of_death_runtime_rule_assignments(
                bringer_of_death_state
            )
        )

    return tuple(assignments)

def get_effective_runtime_rule_assignments(
    configured_profile: ConfiguredProfile,
    *,
    torturer_state: TorturerState | None = None,
    shattered_spirit_state: ShatteredSpiritState | None = None,
    bringer_of_death_state: BringerOfDeathState | None = None,
) -> tuple[RuntimeSpecialRuleAssignment, ...]:
    static_rule_ids = frozenset(
        assignment.rule.id
        for assignment
        in configured_profile.effective_special_rules
    )

    return get_runtime_granted_rule_assignments(
        static_rule_ids,
        torturer_state=torturer_state,
        shattered_spirit_state=shattered_spirit_state,
        bringer_of_death_state=bringer_of_death_state,
    )
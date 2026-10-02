from configured_profile import ConfiguredProfile
from torturer_runtime_rules import (
    get_torturer_runtime_rule_ids,
)
from torturer_state import TorturerState


from configured_profile import ConfiguredProfile
from torturer_runtime_rules import (
    get_torturer_runtime_rule_ids,
)
from torturer_state import TorturerState


def get_runtime_granted_rule_ids(
    existing_rule_ids: frozenset[str],
    *,
    torturer_state: TorturerState | None = None,
) -> frozenset[str]:
    """
    Returns Special Rule IDs granted dynamically at runtime.

    Static configured rules, Mount rules and other persistent
    sources are resolved elsewhere.
    """

    granted_rule_ids: set[str] = set()

    if (
        torturer_state is not None
        and "TORTURER" in existing_rule_ids
    ):
        granted_rule_ids.update(
            get_torturer_runtime_rule_ids(
                torturer_state
            )
        )

    return frozenset(granted_rule_ids)


def get_effective_runtime_rule_ids(
    configured_profile: ConfiguredProfile,
    *,
    torturer_state: TorturerState | None = None,
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
        )
    )
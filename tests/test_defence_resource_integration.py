"""DEV-077S-I2-C-G6: Defensive resource integration tests."""

import pytest

from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from configured_profile import ConfiguredProfile
from defensive_state import DefensiveState
from profile_defensive_combat_score import (
    calculate_profile_defensive_combat_score,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from database.rule_category import RuleCategory
from special_rule_defensive_effect import (
    get_available_fate_attempts,
)


def create_defender(
    *,
    will: int = 0,
    fate: int = 0,
    rule_id: str | None = None,
) -> ConfiguredProfile:
    profile = Profile(
        id="RESOURCE_TEST",
        name="Defensive Resource Test",
        points=100,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=will,
        fate=fate,
        max_in_army=1,
    )

    if rule_id is not None:
        profile.special_rules.append(
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(
                    id=rule_id,
                    name=rule_id,
                    category=RuleCategory.SPECIAL,
                ),
                parameter=None,
            )
        )

    return ConfiguredProfile(profile=profile)


def score(defender):
    return calculate_profile_defensive_combat_score(
        defender,
        DEFAULT_COMBAT_BENCHMARK,
        engagements=3,
    )


@pytest.mark.parametrize(
    "rule_id",
    [
        "WILL_OF_THE_NECROMANCER",
        "HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
    ],
)
def test_resource_resolver_recognises_will_as_fate(rule_id):
    defender = create_defender(
        will=2,
        fate=1,
        rule_id=rule_id,
    )

    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=1,
        remaining_will=2,
    )

    assert get_available_fate_attempts(
        defender,
        state,
    ) == 3


def test_ordinary_will_does_not_count_as_fate():
    defender = create_defender(will=2, fate=0)

    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=0,
        remaining_will=2,
    )

    assert get_available_fate_attempts(
        defender,
        state,
    ) == 0


@pytest.mark.parametrize(
    "rule_id",
    [
        "WILL_OF_THE_NECROMANCER",
        "HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
    ],
)
def test_will_as_fate_improves_repeated_survival(rule_id):
    ordinary = create_defender(will=2)
    protected = create_defender(
        will=2,
        rule_id=rule_id,
    )

    assert score(protected) > score(ordinary)


def test_will_without_permission_gives_no_survival_bonus():
    no_will = create_defender(will=0)
    ordinary_will = create_defender(will=2)

    assert score(ordinary_will) == pytest.approx(
        score(no_will)
    )


def test_limited_will_does_not_give_perfect_protection():
    defender = create_defender(
        will=1,
        rule_id="WILL_OF_THE_NECROMANCER",
    )

    assert 0 < score(defender) < 1
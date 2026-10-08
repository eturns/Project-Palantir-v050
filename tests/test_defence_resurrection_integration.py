"""DEV-077S-I2-C-G7-A resurrection integration regression.

Tests existing resurrection mechanics and establishes the
requirement for resurrection-aware defensive recovery.

No production implementation is introduced here.
"""

from fractions import Fraction

import pytest

from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from configured_profile import ConfiguredProfile
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from resurrection_probability import (
    get_resurrection_success_probability,
    get_resurrection_probability_with_master_of_the_nazgul,
)
from resurrection_resolution import (
    get_state_after_model_is_slain,
    get_resurrection_outcome_probabilities,
)
from resurrection_state import ResurrectionState
from profile_defensive_combat_score import (
    calculate_profile_defensive_combat_score,
)
from database.rule_category import RuleCategory
from special_rule import SpecialRule


def create_test_defender(
    *,
    resurrection: bool = False,
) -> ConfiguredProfile:
    profile = Profile(
        id="TEST_NAZGUL" if resurrection else "TEST_NORMAL",
        name="Test Defender",
        points=80,
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
        will=0,
        fate=0,
        max_in_army=1,
    )

    if resurrection:
        profile.special_rules.append(
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(
                    id="UNHOLY_RESURRECTION",
                    name="Unholy Resurrection",
                    category=RuleCategory.SPECIAL,
                ),
                parameter=None,
            )
        )

    return ConfiguredProfile(profile=profile)


def test_ordinary_model_becomes_casualty():
    assert get_state_after_model_is_slain(
        has_unholy_resurrection=False,
    ) is ResurrectionState.CASUALTY


def test_unholy_resurrection_creates_marker():
    assert get_state_after_model_is_slain(
        has_unholy_resurrection=True,
    ) is ResurrectionState.MARKER


def test_baseline_resurrection_probability():
    assert get_resurrection_success_probability() == Fraction(
        2, 3
    )


def test_resurrection_outcomes_sum_to_one():
    outcomes = get_resurrection_outcome_probabilities()

    assert (
        outcomes[ResurrectionState.ALIVE]
        + outcomes[ResurrectionState.CASUALTY]
    ) == Fraction(1, 1)


def test_resurrection_modifier_changes_probability():
    baseline = get_resurrection_success_probability()

    penalised = get_resurrection_success_probability(
        roll_modifier=-1,
    )

    assert penalised < baseline


def test_master_of_nazgul_support_uses_existing_resolver(
    monkeypatch,
):
    import resurrection_probability as module

    calls = []

    def fake_modifier(
        remaining_will,
        distance_inches,
    ):
        calls.append((remaining_will, distance_inches))
        return 1

    monkeypatch.setattr(
        module,
        "get_master_of_the_nazgul_resurrection_modifier",
        fake_modifier,
    )

    result = (
        get_resurrection_probability_with_master_of_the_nazgul(
            necromancer_remaining_will=10,
            distance_inches=3.0,
        )
    )

    assert calls == [(10, 3.0)]
    assert result == Fraction(5, 6)


def test_resurrection_requires_recovery_not_extra_wounds():
    ordinary = create_test_defender(
        resurrection=False,
    )
    nazgul = create_test_defender(
        resurrection=True,
    )

    ordinary_survival = calculate_profile_defensive_combat_score(
        ordinary,
        DEFAULT_COMBAT_BENCHMARK,
        engagements=3,
    )

    nazgul_combat_survival = calculate_profile_defensive_combat_score(
        nazgul,
        DEFAULT_COMBAT_BENCHMARK,
        engagements=3,
    )

    # Unholy Resurrection does not prevent combat wounds.
    # Its recovery benefit belongs after a model is slain.
    assert nazgul_combat_survival == pytest.approx(
        ordinary_survival
    )


def test_resurrection_recovery_improves_effective_presence():
    ordinary = create_test_defender(
        resurrection=False,
    )
    nazgul = create_test_defender(
        resurrection=True,
    )

    ordinary_survival = calculate_profile_defensive_combat_score(
        ordinary,
        DEFAULT_COMBAT_BENCHMARK,
        engagements=3,
    )

    nazgul_presence = calculate_profile_defensive_combat_score(
        nazgul,
        DEFAULT_COMBAT_BENCHMARK,
        engagements=3,
        include_resurrection=True,
    )

    assert nazgul_presence > ordinary_survival
    assert nazgul_presence <= 1.0

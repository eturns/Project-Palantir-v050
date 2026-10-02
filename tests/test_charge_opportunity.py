import pytest

from charge_opportunity import (
    calculate_charge_weighted_duel_probability,
)
from configured_duel_probability import (
    calculate_configured_duel_probability,
)
from configured_profile import ConfiguredProfile
from combat_context import (
    CombatContext,
    EngagementRole,
)
from database.rule_category import RuleCategory
from profile_classification import ModelType
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule


def make_profile(
    profile_id: str,
    *,
    attacks: int = 1,
    cavalry: bool = False,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=10,
        movement=6,
        fight=3,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=attacks,
        wounds=1,
        courage="7+",
        intelligence="7+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={
            (
                ModelType.CAVALRY
                if cavalry
                else ModelType.INFANTRY
            ),
        },
    )


def add_rule(
    profile: Profile,
    rule_id: str,
) -> None:
    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id=rule_id,
                name=rule_id,
                category=RuleCategory.SPECIAL,
            ),
        )
    )


def test_zero_charge_probability_matches_not_charged_duel():
    attacker = ConfiguredProfile(
        profile=make_profile(
            "ATTACKER",
        ),
    )

    defender = ConfiguredProfile(
        profile=make_profile(
            "DEFENDER",
        ),
    )

    expected = calculate_configured_duel_probability(
        attacker,
        defender,
        attacker_context=CombatContext(
            engagement_role=(
                EngagementRole.WAS_CHARGED
            ),
        ),
    )

    result = calculate_charge_weighted_duel_probability(
        attacker,
        defender,
        charge_probability=0.0,
    )

    assert (
        result.attacker_win_probability
        == pytest.approx(
            expected.attacker_win_probability
        )
    )

    assert (
        result.defender_win_probability
        == pytest.approx(
            expected.defender_win_probability
        )
    )

    assert (
        result.draw_probability
        == pytest.approx(
            expected.draw_probability
        )
    )


def test_savage_hunters_full_charge_probability_matches_charged_duel():
    attacker_profile = make_profile(
        "HUNTER_ORC",
    )

    add_rule(
        attacker_profile,
        "SAVAGE_HUNTERS",
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=make_profile(
            "DEFENDER",
        ),
    )

    expected = calculate_configured_duel_probability(
        attacker,
        defender,
        attacker_context=CombatContext(
            engagement_role=(
                EngagementRole.CHARGED
            ),
        ),
    )

    result = calculate_charge_weighted_duel_probability(
        attacker,
        defender,
        charge_probability=1.0,
    )

    assert (
        result.attacker_win_probability
        == pytest.approx(
            expected.attacker_win_probability
        )
    )

    assert (
        result.defender_win_probability
        == pytest.approx(
            expected.defender_win_probability
        )
    )

    assert (
        result.draw_probability
        == pytest.approx(
            expected.draw_probability
        )
    )


def test_partial_charge_probability_lies_between_charge_states():
    attacker_profile = make_profile(
        "HUNTER_ORC",
    )

    add_rule(
        attacker_profile,
        "SAVAGE_HUNTERS",
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=make_profile(
            "DEFENDER",
        ),
    )

    never_charges = (
        calculate_charge_weighted_duel_probability(
            attacker,
            defender,
            charge_probability=0.0,
        )
    )

    always_charges = (
        calculate_charge_weighted_duel_probability(
            attacker,
            defender,
            charge_probability=1.0,
        )
    )

    weighted = (
        calculate_charge_weighted_duel_probability(
            attacker,
            defender,
            charge_probability=0.5,
        )
    )

    assert (
        never_charges.attacker_win_probability
        < weighted.attacker_win_probability
        < always_charges.attacker_win_probability
    )


def test_cavalry_eligibility_probability_weights_extra_attack():
    attacker = ConfiguredProfile(
        profile=make_profile(
            "CAVALRY",
            cavalry=True,
        ),
    )

    defender = ConfiguredProfile(
        profile=make_profile(
            "INFANTRY",
        ),
    )

    no_bonus = (
        calculate_charge_weighted_duel_probability(
            attacker,
            defender,
            charge_probability=1.0,
            cavalry_charge_eligibility_probability=0.0,
        )
    )

    full_bonus = (
        calculate_charge_weighted_duel_probability(
            attacker,
            defender,
            charge_probability=1.0,
            cavalry_charge_eligibility_probability=1.0,
        )
    )

    partial = (
        calculate_charge_weighted_duel_probability(
            attacker,
            defender,
            charge_probability=1.0,
            cavalry_charge_eligibility_probability=0.5,
        )
    )

    assert (
        no_bonus.attacker_win_probability
        < partial.attacker_win_probability
        < full_bonus.attacker_win_probability
    )


def test_mounted_savage_hunter_can_receive_both_charge_bonuses():
    attacker_profile = make_profile(
        "HUNTER_WARG_RIDER",
        cavalry=True,
    )

    add_rule(
        attacker_profile,
        "SAVAGE_HUNTERS",
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=make_profile(
            "INFANTRY",
        ),
    )

    savage_only = (
        calculate_charge_weighted_duel_probability(
            attacker,
            defender,
            charge_probability=1.0,
            cavalry_charge_eligibility_probability=0.0,
        )
    )

    savage_and_cavalry = (
        calculate_charge_weighted_duel_probability(
            attacker,
            defender,
            charge_probability=1.0,
            cavalry_charge_eligibility_probability=1.0,
        )
    )

    assert (
        savage_and_cavalry.attacker_win_probability
        > savage_only.attacker_win_probability
    )


@pytest.mark.parametrize(
    "charge_probability",
    (-0.1, 1.1),
)
def test_rejects_invalid_charge_probability(
    charge_probability,
):
    attacker = ConfiguredProfile(
        profile=make_profile(
            "ATTACKER",
        ),
    )

    defender = ConfiguredProfile(
        profile=make_profile(
            "DEFENDER",
        ),
    )

    with pytest.raises(ValueError):
        calculate_charge_weighted_duel_probability(
            attacker,
            defender,
            charge_probability=charge_probability,
        )
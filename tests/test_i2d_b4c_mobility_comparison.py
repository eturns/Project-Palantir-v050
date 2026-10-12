import pytest

from army import Army
from profiles import Profile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from special_rule import SpecialRule
from ability_tag_entity import AbilityTagEntity
from ability_tag_assignment import AbilityTagAssignment
from mobility_mechanical_comparison import compare_army_mobility


def make_profile(name, movement=6, base=25, rule=None, weight=None):
    profile = Profile(
        id=name, name=name, points=20, movement=movement, base_size_mm=base,
        fight=3, shooting="4+", strength=3, defence=4, attacks=1,
        wounds=1, courage="6+", intelligence="7+", might=0, will=0,
        fate=0, max_in_army=0,
    )
    if rule:
        special = SpecialRule(id=rule, name=rule, category=RuleCategory.MOVEMENT)
        if weight is not None:
            special.ability_tags.append(
                AbilityTagAssignment(tag=AbilityTagEntity(id="MOBILITY", name="Mobility"), weight=weight)
            )
        profile.special_rules.append(ProfileSpecialRuleAssignment(rule=special))
    return profile


def test_baseline_has_no_legacy_delta():
    army = Army()
    army.add_profile(make_profile("REGULAR"), quantity=2)
    result = compare_army_mobility(army)
    assert result.model_count == 2
    assert result.legacy_manoeuvrability == pytest.approx(6)
    assert result.open_ground_manoeuvrability == pytest.approx(6)
    assert result.difficult_terrain_manoeuvrability == pytest.approx(3)
    assert result.legacy_minus_open_ground == pytest.approx(0)
    assert result.has_special_reposition is False


def test_larger_base_penalty_preserved_in_mechanical_comparison():
    army = Army()
    army.add_profile(make_profile("LARGE", base=60))
    result = compare_army_mobility(army)
    assert result.open_ground_manoeuvrability < 6
    assert result.difficult_terrain_manoeuvrability < 3


def test_unnatural_speed_is_reported_without_invented_move_inches():
    army = Army()
    army.add_profile(make_profile("SHADOW", rule="UNNATURAL_SPEED", weight=1.5))
    result = compare_army_mobility(army)
    assert result.self_reposition_models == 1
    assert result.legacy_minus_open_ground == pytest.approx(1.5)
    assert result.open_ground_manoeuvrability == pytest.approx(6)


def test_anchor_reposition_requires_two_models():
    alone = Army()
    alone.add_profile(make_profile("KNIGHT", rule="SPIRITUAL_DISPLACEMENT", weight=1.5))
    assert compare_army_mobility(alone).eligible_anchor_pairs == 0

    paired = Army()
    paired.add_profile(make_profile("KNIGHT", rule="SPIRITUAL_DISPLACEMENT", weight=1.5), quantity=2)
    result = compare_army_mobility(paired)
    assert result.anchor_reposition_models == 2
    assert result.eligible_anchor_pairs == 1
    assert result.legacy_minus_open_ground == pytest.approx(0.75)


def test_legacy_tag_and_terrain_mechanics_are_separate():
    army = Army()
    army.add_profile(make_profile("SPECTRE", rule="SPECTRAL_WALK", weight=1.5))
    result = compare_army_mobility(army)
    assert result.legacy_minus_open_ground == pytest.approx(1.5)
    assert result.difficult_terrain_manoeuvrability == pytest.approx(6)
    assert dict(result.terrain_rule_model_counts)["SPECTRAL_WALK"] == 1


def test_empty_army_is_valid_diagnostic():
    result = compare_army_mobility(Army())
    assert result.model_count == 0
    assert result.open_ground_manoeuvrability == 0
    assert result.eligible_anchor_pairs == 0

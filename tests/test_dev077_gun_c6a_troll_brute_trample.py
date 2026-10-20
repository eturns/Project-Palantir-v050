"""DEV-077-GUN-C6-A focused Troll Brute impact tests."""
from fractions import Fraction
from types import SimpleNamespace

import pytest

from gundabad_troll_brute_trample import (
    ImpactComponent, has_troll_brute_trample,
    resolve_troll_brute_impact_hits, trample_continues_after_contact,
)


def brute(profile_id="TROLL_BRUTE", rule="TRAMPLE"):
    return SimpleNamespace(
        profile=SimpleNamespace(id=profile_id),
        effective_special_rules=(SimpleNamespace(rule=SimpleNamespace(id=rule)),),
    )


def test_brute_has_trample():
    assert has_troll_brute_trample(brute())


def test_orc_commander_does_not_get_troll_impacts():
    assert not has_troll_brute_trample(brute(profile_id="ORC_COMMANDER"))


def test_missing_rule_is_not_implicitly_granted():
    assert not has_troll_brute_trample(brute(rule="TERROR"))


def test_two_strength_ten_hits_against_defence_four():
    (result,) = resolve_troll_brute_impact_hits(
        brute(), (ImpactComponent("orc", 4),), is_trampling=True
    )
    assert (result.strength, result.hit_count) == (10, 2)
    assert result.wound_probability_per_hit == Fraction(2, 3)
    assert result.expected_raw_wounds == Fraction(4, 3)
    assert result.raw_wound_distribution == (
        Fraction(1, 9), Fraction(4, 9), Fraction(4, 9)
    )


def test_high_defence_uses_shared_wound_table():
    (result,) = resolve_troll_brute_impact_hits(
        brute(), (ImpactComponent("armoured", 10),), is_trampling=True
    )
    assert result.wound_probability_per_hit == Fraction(1, 2)


def test_cavalry_rider_and_mount_each_take_two_hits():
    results = resolve_troll_brute_impact_hits(
        brute(), (ImpactComponent("rider", 6), ImpactComponent("mount", 4)),
        is_trampling=True,
    )
    assert len(results) == 2
    assert [v.hit_count for v in results] == [2, 2]


def test_not_trampling_means_no_impacts():
    assert resolve_troll_brute_impact_hits(
        brute(), (ImpactComponent("orc", 4),), is_trampling=False
    ) == ()


def test_wrong_model_means_no_impacts():
    assert resolve_troll_brute_impact_hits(
        brute(profile_id="WAR_BAT"),
        (ImpactComponent("orc", 4),), is_trampling=True
    ) == ()


def test_form_state_can_be_used():
    state = SimpleNamespace(active_configured_profile=brute())
    assert has_troll_brute_trample(state)


def test_duplicate_component_refused():
    with pytest.raises(ValueError):
        resolve_troll_brute_impact_hits(
            brute(), (ImpactComponent("x", 4), ImpactComponent("x", 5)),
            is_trampling=True,
        )


def test_invalid_defence_refused():
    with pytest.raises(ValueError):
        ImpactComponent("x", 11)


def test_empty_component_id_refused():
    with pytest.raises(ValueError):
        ImpactComponent("", 4)


def test_wrong_context_flag_type_refused():
    with pytest.raises(TypeError):
        resolve_troll_brute_impact_hits(brute(), (), is_trampling=1)


def test_continues_only_when_target_slain():
    assert trample_continues_after_contact(target_survived=False)
    assert not trample_continues_after_contact(target_survived=True)


def test_no_inferred_survival():
    with pytest.raises(TypeError):
        trample_continues_after_contact(target_survived=None)

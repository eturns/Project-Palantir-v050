"""DEV-077-SMAUG-C2C/E — bounded aggregate shooting integration tests."""
from fractions import Fraction
import pytest

from defensive_state import DefensiveState
from smaug_breathe_fire import FireVictim
from wound_table import get_wound_target
from wound_probability import get_wound_probability
from smaug_fire_defensive_resolution import FireDefender
from smaug_fire_shooting_evidence import calculate_smaug_fire_shooting_evidence


def shot(victims, defenders, *, distance=18, source="SMAUG"):
    return calculate_smaug_fire_shooting_evidence(
        source_profile_id=source, target_distance_inches=distance,
        primary_target_id="primary", victims=tuple(victims), defenders=tuple(defenders),
    )


def victim(name, defence=1, gap=0, immune=False):
    return FireVictim(name, defence, gap, immune)


def defender(name, fate=0):
    return FireDefender(name, DefensiveState(remaining_wounds=2, remaining_fate=fate))


def test_single_shot_multiple_targets_linear_expectations_not_extra_attacks():
    evidence = shot([victim("primary"), victim("splash", gap=2)],
                    [defender("primary"), defender("splash")])
    assert evidence.attacks == 1
    assert evidence.target_count == 2
    assert evidence.probability_primary_hit == Fraction(5, 6)
    assert evidence.expected_immediate_casualties == 2 * Fraction(5, 6) * get_wound_probability(get_wound_target(10, 1))
    assert evidence.expected_models_set_ablaze == 2 * (Fraction(5, 6) - Fraction(5, 6) * get_wound_probability(get_wound_target(10, 1)))


def test_fate_prevents_instant_kill_and_causes_set_ablaze():
    evidence = shot([victim("primary")], [defender("primary", fate=1)])
    wounded = Fraction(5, 6) * get_wound_probability(get_wound_target(10, 1))
    assert evidence.expected_wounds_before_prevention == wounded
    assert evidence.expected_prevented_wounds == wounded / 2
    assert evidence.expected_immediate_casualties == wounded / 2
    assert evidence.expected_models_set_ablaze == Fraction(5, 6) - wounded / 2


def test_fire_immunity_zeroes_target_contributions():
    evidence = shot([victim("primary", immune=True)], [defender("primary")])
    assert evidence.expected_immediate_casualties == 0
    assert evidence.expected_models_set_ablaze == 0
    assert evidence.target_count == 1


def test_outside_radius_excluded_even_if_defender_supplied_only_for_impacted():
    evidence = shot([victim("primary"), victim("far", gap=2.01)], [defender("primary")])
    assert evidence.target_count == 1


def test_outside_range_gives_zero_expected_values():
    evidence = shot([victim("primary")], [defender("primary")], distance=18.01)
    assert evidence.expected_immediate_casualties == 0
    assert evidence.expected_models_set_ablaze == 0
    assert evidence.attacks == 1


def test_non_smaug_source_rejected():
    with pytest.raises(ValueError, match="SMAUG"):
        shot([victim("primary")], [defender("primary")], source="TT_BILL")


def test_missing_defender_rejected_rather_than_estimated():
    with pytest.raises(ValueError, match="exactly one defence state"):
        shot([victim("primary")], [])


def test_no_false_probability_of_group_elimination_exposed():
    evidence = shot([victim("primary"), victim("splash", gap=1)],
                    [defender("primary"), defender("splash")])
    assert not hasattr(evidence, "probability_all_slain")
    assert evidence.evidence_status.startswith("bounded_")

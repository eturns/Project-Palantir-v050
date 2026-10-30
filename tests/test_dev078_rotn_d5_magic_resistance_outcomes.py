"""DEV-078-ROTN-D5: Rules Manual 2024 resistance probability contracts."""
import pytest
from magic_resistance_outcomes import resolve_magic_resistance as resist


def test_free_die_at_zero_will():
    r = resist(cast_highest=4, will_available=0, resistant_to_magic=True)
    assert (r.dice_total, r.will_after_spend) == (1, 0)
    assert r.probability_resisted == pytest.approx(0.5)


def test_resistance_does_not_require_paid_die():
    r = resist(cast_highest=5, will_available=3, resistant_to_magic=True)
    assert r.will_spent == 0
    assert r.probability_resisted == pytest.approx(2 / 6)


def test_paid_and_free_dice():
    r = resist(cast_highest=4, will_available=3, will_spent=2,
               resistant_to_magic=True, hero=True)
    assert (r.dice_total, r.will_after_spend) == (3, 1)
    assert r.probability_resisted == pytest.approx(1 - (3/6)**3)
    assert r.expected_hero_will_refund == pytest.approx(2/6)


def test_free_die_never_refunds_will():
    r = resist(cast_highest=6, will_available=0, resistant_to_magic=True, hero=True)
    assert r.expected_hero_will_refund == 0


def test_normal_paid_resistance():
    r = resist(cast_highest=5, will_available=2, will_spent=1)
    assert r.dice_total == 1
    assert r.probability_resisted == pytest.approx(2/6)


def test_no_dice_means_no_resistance():
    assert resist(cast_highest=4, will_available=0).probability_resisted == 0


def test_cumulative_different_free_sources():
    r = resist(cast_highest=4, will_available=0, resistant_to_magic=True,
               other_free_die_sources=("HEROIC_RESOLVE",))
    assert r.dice_total == 2
    assert r.probability_resisted == pytest.approx(0.75)


def test_duplicate_source_cannot_double_count():
    with pytest.raises(ValueError):
        resist(cast_highest=4, will_available=0, resistant_to_magic=True,
               other_free_die_sources=("RESISTANT_TO_MAGIC",))


def test_duplicate_other_sources_rejected():
    with pytest.raises(ValueError):
        resist(cast_highest=4, will_available=0,
               other_free_die_sources=("X", "X"))


def test_indirect_effect_cannot_be_resisted():
    with pytest.raises(ValueError):
        resist(cast_highest=4, will_available=1, will_spent=1,
               directly_targeted=False)


@pytest.mark.parametrize("value", [0, 7, True, 3.5])
def test_bad_cast_roll_rejected(value):
    with pytest.raises((ValueError, TypeError)):
        resist(cast_highest=value, will_available=1)


@pytest.mark.parametrize("available,spent", [(0,1), (-1,0), (2,-1), (True,0)])
def test_invalid_will_rejected(available, spent):
    with pytest.raises((ValueError, TypeError)):
        resist(cast_highest=4, will_available=available, will_spent=spent)


def test_hero_refund_only_paid_dice():
    r = resist(cast_highest=6, will_available=6, will_spent=2,
               other_free_die_sources=("A", "B"), hero=True)
    assert r.expected_hero_will_refund == pytest.approx(1/3)
    assert r.expected_will_after_refund == pytest.approx(4 + 1/3)


def test_nonhero_gets_no_refund():
    r = resist(cast_highest=6, will_available=2, will_spent=2)
    assert r.expected_hero_will_refund == 0


def test_scores_are_never_supplied():
    r = resist(cast_highest=3, will_available=1, will_spent=1)
    assert r.dashboard_score is None and r.scenario_score is None

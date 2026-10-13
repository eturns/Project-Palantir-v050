"""F2-A4 tests: shared Will, declared opportunities, provenance and score isolation."""
from dataclasses import replace

import pytest

from mechanical_magic_casting import enumerate_cast_allocations
from mechanical_magic_sequence import PlannedMagicCast, calculate_magic_casting_sequence
from mechanical_magic_spell_profiles import ProfileMagicCastingEvidence, SpellCastingOptions


def evidence(will=4, extra=False):
    spells = []
    for spell_id, value in (("TRANSFIX", 3), ("CHILL_SOUL", 5)):
        spells.append(SpellCastingOptions(
            spell_id=spell_id, spell_name=spell_id, cast_value=value,
            allocations=enumerate_cast_allocations(cast_value=value, will_available=will),
            conditional_rule_ids=(),
        ))
    if extra:
        spells.append(SpellCastingOptions(
            spell_id="TRANSFIX", spell_name="TRANSFIX", cast_value=3,
            allocations=enumerate_cast_allocations(
                cast_value=3, will_available=will,
                additional_dice=1, extra_dice_source="EXPLICIT_TEST_RULE",
            ),
            conditional_rule_ids=("EXPLICIT_TEST_RULE",),
        ))
    return ProfileMagicCastingEvidence(
        profile_id="TEST", will_available=will,
        spell_options=tuple(spells), excluded_spell_ids=(),
        conditional_extra_casting_dice=int(extra),
        conditional_extra_casting_dice_sources=("EXPLICIT_TEST_RULE",) if extra else (),
        conditional_extra_casts_per_opportunity=0,
        conditional_extra_cast_sources=(),
    )


def plan(e, index, spend, verified=False):
    return PlannedMagicCast(e.spell_options[index], spend, verified)


def run(e, *casts, slots=None):
    return calculate_magic_casting_sequence(e, tuple(casts), permitted_cast_slots=(len(casts) if slots is None else slots))


def test_two_different_spells_consume_one_shared_pool():
    e = evidence(4)
    result = run(e, plan(e, 0, 1), plan(e, 1, 2))
    assert result.spell_ids == ("TRANSFIX", "CHILL_SOUL")
    assert [a.will_available for a in result.attempts] == [4, 3]
    assert [a.will_remaining_after_attempt for a in result.attempts] == [3, 1]
    assert (result.spent_will, result.remaining_will) == (3, 1)
    assert result.expected_successes == pytest.approx(2/3 + 5/9)


def test_single_cast_with_more_slots_does_not_imply_more_attempts():
    e = evidence()
    result = run(e, plan(e, 0, 1), slots=3)
    assert len(result.attempts) == 1
    assert result.expected_successes == pytest.approx(2/3)


def test_repeat_spell_is_permitted_only_as_explicit_generic_input():
    e = evidence()
    r = run(e, plan(e, 0, 1), plan(e, 0, 1))
    assert r.spell_ids == ("TRANSFIX", "TRANSFIX")
    assert r.remaining_will == 2


def test_cast_slots_limit_is_enforced():
    e = evidence()
    with pytest.raises(ValueError, match="permitted_cast_slots"):
        run(e, plan(e, 0, 1), plan(e, 1, 1), slots=1)


def test_no_will_overspend_even_if_slots_allow():
    e = evidence(1)
    with pytest.raises(ValueError, match="insufficient remaining Will"):
        run(e, plan(e, 0, 1), plan(e, 1, 1))


def test_each_cast_uses_current_pool_not_initial_pool():
    e = evidence(3)
    r = run(e, plan(e, 0, 2), plan(e, 1, 1))
    assert r.remaining_will == 0
    assert r.attempts[1].will_available == 1


def test_conditional_dice_requires_verification():
    e = evidence(extra=True)
    with pytest.raises(ValueError, match="verification"):
        run(e, plan(e, 2, 1))


def test_conditional_extra_die_changes_probability_not_will_spent():
    e = evidence(extra=True)
    r = run(e, plan(e, 2, 1, True), plan(e, 0, 1))
    assert [a.will_spent for a in r.attempts] == [1, 1]
    assert [a.probability for a in r.attempts] == pytest.approx([8/9, 2/3])
    assert r.remaining_will == 2


def test_no_planned_casts_is_valid():
    e = evidence()
    r = run(e, slots=2)
    assert r.attempts == ()
    assert r.remaining_will == 4
    assert r.expected_successes == 0


def test_zero_will_empty_plan_is_valid():
    e = evidence(0)
    assert run(e, slots=1).remaining_will == 0


def test_zero_will_cannot_cast():
    e = evidence(0)
    with pytest.raises(ValueError, match="insufficient remaining Will"):
        run(e, plan(e, 0, 1))


def test_foreign_option_is_rejected():
    a, b = evidence(), evidence()
    with pytest.raises(ValueError, match="does not belong"):
        run(a, plan(b, 0, 1))


@pytest.mark.parametrize("bad", [True, 1.3, -1, "2"])
def test_invalid_slots(bad):
    with pytest.raises((ValueError, TypeError)):
        run(evidence(), slots=bad)


@pytest.mark.parametrize("bad", [0, -1, True, 1.2])
def test_invalid_will_allocation(bad):
    e = evidence()
    with pytest.raises((ValueError, TypeError)):
        run(e, plan(e, 0, bad))


def test_invalid_verification_type():
    e = evidence(extra=True)
    with pytest.raises(TypeError, match="conditional_rules_verified"):
        run(e, plan(e, 2, 1, "yes"))


def test_unavailable_spell_allocation_rejected():
    e = evidence(2)
    option = replace(e.spell_options[0], allocations=())
    mutated = replace(e, spell_options=(option, e.spell_options[1]))
    with pytest.raises(ValueError, match="unavailable"):
        run(mutated, plan(mutated, 0, 1))


def test_scores_are_not_produced():
    e = evidence()
    r = run(e, plan(e, 0, 1))
    assert r.dashboard_score is None and r.scenario_score is None
    assert r.evidence_status == "diagnostic_not_calibrated"


def test_strict_tuple_plan_required():
    with pytest.raises(TypeError, match="tuple"):
        calculate_magic_casting_sequence(evidence(), [], permitted_cast_slots=1)

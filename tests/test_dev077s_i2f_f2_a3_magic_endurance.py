"""DEV-077S-I2-F2-A3: budget boundaries and conditional casting."""
from dataclasses import replace
from types import SimpleNamespace

import pytest

from mechanical_magic_endurance import calculate_magic_endurance
from mechanical_magic_spell_profiles import build_profile_magic_casting_evidence
from profile_spell_assignment import ProfileSpellAssignment
from profiles import Profile
from spell import Spell
from database.rule_category import RuleCategory


def evidence(will=3, profile_id="CASTER", rules=()):
    spell = Spell(id="TEST_SPELL", name="Test Spell", category=RuleCategory.COMMAND)
    profile = Profile(
        id=profile_id, name="Caster", points=100, movement=6, fight=4,
        shooting="4+", strength=4, defence=5, attacks=1, wounds=2,
        courage="6+", intelligence="6+", might=1, will=will, fate=1,
        max_in_army=1,
        spells=[ProfileSpellAssignment(spell=spell, cast_value=3)],
    )
    kwargs = (
        {"army": object(), "army_list": SimpleNamespace(
            army_rules=[SimpleNamespace(id=rule) for rule in rules]
        )} if rules else {}
    )
    return build_profile_magic_casting_evidence(profile, **kwargs)


def assess(e, *, index=0, spend=1, windows=5, verify=False):
    return calculate_magic_endurance(
        e, e.spell_options[index], will_per_attempt=spend,
        hypothetical_opportunities=windows,
        verify_conditional_rules=verify,
    )


def test_resource_limited_three_single_die_attempts():
    r = assess(evidence(), spend=1, windows=10)
    assert (r.resource_affordable_attempts, r.modelled_attempts) == (3, 3)
    assert (r.will_consumed, r.will_remaining) == (3, 0)
    assert r.expected_successful_casts == pytest.approx(2.0)


def test_two_will_each_allows_one_attempt_and_remainder():
    r = assess(evidence(), spend=2, windows=10)
    assert r.modelled_attempts == 1
    assert r.will_remaining == 1
    assert r.probability_per_attempt == pytest.approx(8/9)
    assert r.expected_successful_casts == pytest.approx(8/9)


def test_opportunity_limited_does_not_spend_unchosen_will():
    r = assess(evidence(), windows=1)
    assert r.modelled_attempts == 1
    assert r.will_remaining == 2
    assert r.expected_successful_casts == pytest.approx(2/3)


def test_zero_opportunities_preserves_budget():
    r = assess(evidence(), windows=0)
    assert r.modelled_attempts == 0
    assert r.probability_per_attempt == 0
    assert r.expected_successful_casts == 0
    assert r.will_remaining == 3


def test_zero_will_yields_zero_affordable_attempts():
    r = assess(evidence(will=0), windows=10)
    assert (r.resource_affordable_attempts, r.modelled_attempts) == (0, 0)
    assert r.will_remaining == 0


def test_conditional_extra_die_requires_verification():
    e = evidence(profile_id="DG_NEC", rules=("DG_HIS_SPIRIT",))
    with pytest.raises(ValueError, match="verification"):
        assess(e, index=1)


def test_conditional_die_increases_reliability_but_not_will():
    e = evidence(profile_id="DG_NEC", rules=("DG_HIS_SPIRIT",))
    base = assess(e, windows=3)
    boosted = assess(e, index=1, windows=3, verify=True)
    assert boosted.probability_per_attempt == pytest.approx(8/9)
    assert boosted.expected_successful_casts == pytest.approx(8/3)
    assert boosted.will_consumed == base.will_consumed == 3
    assert boosted.conditional_rule_ids == ("DG_HIS_SPIRIT",)


def test_extra_cast_rule_does_not_imply_extra_opportunities():
    e = evidence(profile_id="DG_NEC", rules=("DG_POWER_OF_THE_NECROMANCER",))
    r = assess(e, windows=1)
    assert r.modelled_attempts == 1
    assert r.expected_successful_casts == pytest.approx(2/3)


@pytest.mark.parametrize("bad", [0, -1])
def test_invalid_will_spend(bad):
    with pytest.raises(ValueError, match="will_per_attempt"):
        assess(evidence(), spend=bad)


@pytest.mark.parametrize("bad", [True, 1.5, "1"])
def test_invalid_will_spend_type(bad):
    with pytest.raises(TypeError, match="will_per_attempt"):
        assess(evidence(), spend=bad)


@pytest.mark.parametrize("bad", [-1, False, 1.2])
def test_invalid_opportunity_count(bad):
    with pytest.raises((TypeError, ValueError), match="hypothetical_opportunities"):
        assess(evidence(), windows=bad)


def test_unaffordable_fixed_allocation_rejected():
    with pytest.raises(ValueError, match="matching casting allocation"):
        assess(evidence(will=1), spend=2)


def test_foreign_option_rejected_even_for_same_spell():
    a, b = evidence(), evidence()
    with pytest.raises(ValueError, match="belong"):
        calculate_magic_endurance(a, b.spell_options[0],
                                   will_per_attempt=1, hypothetical_opportunities=1)


def test_diagnostic_scores_are_absent():
    r = assess(evidence())
    assert r.dashboard_score is None and r.scenario_score is None
    assert r.evidence_status == "diagnostic_not_calibrated"


def test_cannot_fake_rule_verification_with_string():
    e = evidence(profile_id="DG_NEC", rules=("DG_HIS_SPIRIT",))
    with pytest.raises(TypeError, match="verify_conditional_rules"):
        assess(e, index=1, verify="yes")

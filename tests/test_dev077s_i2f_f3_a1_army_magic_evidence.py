"""F3-A1 quantity-weighted, diagnostic-only army spell inventory tests."""
from math import isclose
import pytest
from army import Army
from database.rule_category import RuleCategory
from spell import Spell
from profile_spell_assignment import ProfileSpellAssignment
from profiles import Profile
from mechanical_magic_army_evidence import build_army_magic_evidence


def profile(identifier, *, will=0, threshold=None, spell_id="SPELL", points=50):
    model = Profile(id=identifier, name=identifier, points=points, movement=6,
                    fight=4, shooting="4+", strength=4, defence=5, attacks=1,
                    wounds=1, courage="6+", intelligence="6+", might=0,
                    will=will, fate=0, max_in_army=0)
    if threshold is not None:
        model.spells.append(ProfileSpellAssignment(
            spell=Spell(id=spell_id, name=spell_id, category=RuleCategory.COMMAND),
            cast_value=threshold,
        ))
    return model


def test_empty_army_no_assumed_reliability():
    r = build_army_magic_evidence(Army())
    assert r.model_count == r.caster_count == r.initial_caster_will == 0
    assert r.one_will_probability_weighted_mean is None
    assert r.caster_will_per_100_points is None
    assert r.dashboard_score is r.scenario_score is None


def test_non_caster_will_not_counted_as_magic():
    army = Army()
    army.add_profile(profile("ordinary", will=4), quantity=3)
    r = build_army_magic_evidence(army)
    assert r.model_count == 3
    assert r.initial_caster_will == 0
    assert r.caster_count == 0
    assert r.one_will_probability_weighted_mean is None


def test_single_spellcaster():
    army = Army()
    army.add_profile(profile("mage", will=3, threshold=3, points=100))
    r = build_army_magic_evidence(army)
    assert r.caster_count == 1
    assert r.initial_caster_will == 3
    assert r.caster_will_per_100_points == 3
    assert r.spell_assignment_count == 1
    assert r.one_will_probability_weighted_mean == pytest.approx(2 / 3)
    assert r.spells[0].caster_model_count == 1


def test_quantities_scale_resources_not_probability():
    army = Army()
    army.add_profile(profile("mage", will=3, threshold=3), quantity=2)
    r = build_army_magic_evidence(army)
    assert r.caster_count == 2
    assert r.initial_caster_will == 6
    assert r.spell_assignment_count == 2
    assert r.spells[0].caster_model_count == 2
    assert r.one_will_probability_weighted_mean == pytest.approx(2 / 3)


def test_weighted_average_keeps_thresholds_separate():
    army = Army()
    army.add_profile(profile("easy", will=1, threshold=3), quantity=2)
    army.add_profile(profile("hard", will=1, threshold=5), quantity=1)
    r = build_army_magic_evidence(army)
    assert r.one_will_probability_weighted_mean == pytest.approx(((2 / 3) * 2 + (1 / 3)) / 3)
    assert {x.cast_value for x in r.spells} == {3, 5}


def test_same_spell_different_thresholds_are_not_collapsed():
    army = Army()
    army.add_profile(profile("a", will=1, threshold=3, spell_id="SHARED"))
    army.add_profile(profile("b", will=1, threshold=5, spell_id="SHARED"))
    r = build_army_magic_evidence(army)
    assert r.unique_spell_ids == ("SHARED",)
    assert len(r.spells) == 2


def test_zero_will_caster_preserves_spell_availability_not_success():
    army = Army()
    army.add_profile(profile("empty", will=0, threshold=3))
    r = build_army_magic_evidence(army)
    assert r.caster_count == 1
    assert r.spells[0].one_will_success_probability is None
    assert r.one_will_probability_weighted_mean is None


def test_non_caster_dilutes_density_not_spell_probability():
    army = Army()
    army.add_profile(profile("mage", will=2, threshold=3, points=50))
    before = build_army_magic_evidence(army)
    army.add_profile(profile("soldier", points=50), quantity=3)
    after = build_army_magic_evidence(army)
    assert after.caster_will_per_100_points < before.caster_will_per_100_points
    assert after.one_will_probability_weighted_mean == before.one_will_probability_weighted_mean


def test_no_legacy_combined_magic_score():
    army = Army()
    army.add_profile(profile("mage", will=2, threshold=3))
    r = build_army_magic_evidence(army)
    assert not hasattr(r, "magic_score")
    assert r.evidence_status == "diagnostic_not_calibrated"


def test_wrong_input_rejected():
    with pytest.raises(TypeError):
        build_army_magic_evidence(object())

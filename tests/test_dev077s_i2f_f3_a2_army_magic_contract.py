"""F3-A2: quantity, separate Will budgets, spell categories, provenance."""
import pytest
from army import Army
from ability_tag_assignment import AbilityTagAssignment
from ability_tag_entity import AbilityTagEntity
from database.rule_category import RuleCategory
from mechanical_magic_army_contract import build_army_magic_contract
from profile_spell_assignment import ProfileSpellAssignment
from profiles import Profile
from spell import Spell


def model(name, will=0, spells=(), points=50):
    p = Profile(id=name, name=name, points=points, movement=6, fight=4,
                shooting="4+", strength=4, defence=5, attacks=1, wounds=1,
                courage="6+", intelligence="6+", might=0, will=will, fate=0,
                max_in_army=0)
    p.spells.extend(spells)
    return p


def spell(name, tags=(), threshold=3):
    s = Spell(id=name, name=name, category=RuleCategory.COMMAND)
    s.ability_tags.extend(
        AbilityTagAssignment(tag=AbilityTagEntity(id=t, name=t), weight=1.0)
        for t in tags
    )
    return ProfileSpellAssignment(spell=s, cast_value=threshold)


def test_empty_army_has_no_probability_or_imaginary_casts():
    r = build_army_magic_contract(Army())
    assert r.caster_count == r.one_will_attempt_ceiling == 0
    assert r.one_will_probability_weighted_mean is None
    assert r.effect_categories == ()


def test_no_caster_will_contribution():
    a = Army()
    a.add_profile(model("fighter", will=6), quantity=3)
    r = build_army_magic_contract(a)
    assert r.starting_caster_will == r.one_will_attempt_ceiling == 0


def test_caster_resource_totals_are_quantity_aware():
    a = Army()
    a.add_profile(model("wizard", 3, (spell("A"),)), quantity=2)
    r = build_army_magic_contract(a)
    assert r.caster_count == 2
    assert r.starting_caster_will == 6
    assert r.one_will_attempt_ceiling == 6
    assert r.caster_groups[0].one_will_attempt_ceiling_per_model == 3


def test_two_casters_keep_separate_resource_groups():
    a = Army()
    a.add_profile(model("caster1", 1, (spell("A"),)))
    a.add_profile(model("caster2", 5, (spell("B"),)))
    r = build_army_magic_contract(a)
    assert [g.initial_will_per_model for g in r.caster_groups] == [1, 5]
    assert [g.available_spell_ids for g in r.caster_groups] == [("A",), ("B",)]


def test_more_spells_do_not_multiply_endurance():
    a = Army()
    a.add_profile(model("caster", 3, (spell("A"), spell("B"), spell("C"))))
    r = build_army_magic_contract(a)
    assert r.one_will_attempt_ceiling == 3
    assert len(r.distinct_spell_ids) == 3


def test_overlapping_tags_are_reported_not_added_as_effects():
    a = Army()
    a.add_profile(model("caster", 2, (spell("A", ("CONTROL", "OFFENCE")),)))
    r = build_army_magic_contract(a)
    assert {c.tag_id for c in r.effect_categories} == {"CONTROL", "OFFENCE"}
    assert all(c.spell_assignment_instances == 1 for c in r.effect_categories)
    assert not hasattr(r, "combined_magic_score")


def test_repeated_models_weight_category_assignments():
    a = Army()
    a.add_profile(model("caster", 2, (spell("A", ("CONTROL",)),)), quantity=3)
    r = build_army_magic_contract(a)
    assert r.effect_categories[0].spell_assignment_instances == 3
    assert r.effect_categories[0].distinct_spell_ids == ("A",)


def test_same_tag_on_multiple_spells_lists_both():
    a = Army()
    a.add_profile(model("caster", 2, (
        spell("A", ("CONTROL",)), spell("B", ("CONTROL",))
    )))
    r = build_army_magic_contract(a)
    assert r.effect_categories[0].distinct_spell_ids == ("A", "B")
    assert r.effect_categories[0].spell_assignment_instances == 2


def test_untagged_spell_remains_in_repertoire():
    a = Army()
    a.add_profile(model("caster", 1, (spell("UNTAGGED"),)))
    r = build_army_magic_contract(a)
    assert r.distinct_spell_ids == ("UNTAGGED",)
    assert r.effect_categories == ()


def test_zero_will_caster_retains_repertoire_not_endurance():
    a = Army()
    a.add_profile(model("caster", 0, (spell("A", ("CONTROL",)),)))
    r = build_army_magic_contract(a)
    assert r.caster_count == 1
    assert r.one_will_attempt_ceiling == 0
    assert r.one_will_probability_weighted_mean is None
    assert len(r.effect_categories) == 1


def test_diagnostic_not_calibrated_and_no_scores():
    a = Army()
    a.add_profile(model("caster", 1, (spell("A"),)))
    r = build_army_magic_contract(a)
    assert r.evidence_status == "diagnostic_not_calibrated"
    assert r.calibration_status == "pending"
    assert r.dashboard_score is None and r.scenario_score is None


def test_non_caster_changes_points_but_not_cast_ceiling():
    a = Army()
    a.add_profile(model("caster", 2, (spell("A"),)))
    before = build_army_magic_contract(a)
    a.add_profile(model("trooper"), quantity=5)
    after = build_army_magic_contract(a)
    assert after.army_points > before.army_points
    assert after.one_will_attempt_ceiling == before.one_will_attempt_ceiling


def test_wrong_input_rejected():
    with pytest.raises(TypeError, match="Army"):
        build_army_magic_contract(object())

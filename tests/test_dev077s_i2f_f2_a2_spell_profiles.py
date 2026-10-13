"""DEV-077S-I2-F2-A2: eligibility, conditional modifiers and resource tests."""
from types import SimpleNamespace

import pytest

from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from mechanical_magic_spell_profiles import build_profile_magic_casting_evidence
from profile_spell_assignment import ProfileSpellAssignment
from profiles import Profile
from spell import Spell


def caster(profile_id="TEST_CASTER", will=3, spells=None):
    return Profile(
        id=profile_id, name="Caster", points=100, movement=6, fight=4,
        shooting="4+", strength=4, defence=5, attacks=1, wounds=2,
        courage="6+", intelligence="6+", might=1, will=will, fate=1,
        max_in_army=1, spells=list(spells or []),
    )


def assigned(spell_id="TRANSFIX", threshold=3, prerequisites=()):
    return ProfileSpellAssignment(
        spell=Spell(
            id=spell_id, name=spell_id.title(),
            category=RuleCategory.COMMAND,
            prerequisites=list(prerequisites),
        ),
        cast_value=threshold,
    )


def rules(*ids):
    return SimpleNamespace(army_rules=[SimpleNamespace(id=rule_id) for rule_id in ids])


def test_one_spell_enumerates_exact_allocations():
    report = build_profile_magic_casting_evidence(caster(spells=[assigned()]))
    assert len(report.spell_options) == 1
    option = report.spell_options[0]
    assert option.spell_id == "TRANSFIX"
    assert [a.will_spent for a in option.allocations] == [1, 2, 3]
    assert [a.probability for a in option.allocations] == pytest.approx([2/3, 8/9, 26/27])
    assert report.dashboard_score is None and report.scenario_score is None


def test_no_spells_is_empty_not_a_guessed_score():
    report = build_profile_magic_casting_evidence(caster())
    assert report.spell_options == ()
    assert report.excluded_spell_ids == ()


def test_zero_will_does_not_fabricate_casts():
    report = build_profile_magic_casting_evidence(caster(will=0, spells=[assigned()]))
    assert len(report.spell_options) == 1
    assert report.spell_options[0].allocations == ()


def test_explicit_remaining_will_limits_allocations():
    report = build_profile_magic_casting_evidence(
        caster(will=5, spells=[assigned()]), remaining_will=1
    )
    assert [a.will_spent for a in report.spell_options[0].allocations] == [1]


def test_configured_profile_supported():
    report = build_profile_magic_casting_evidence(
        ConfiguredProfile(profile=caster(spells=[assigned()]))
    )
    assert report.profile_id == "TEST_CASTER"
    assert len(report.spell_options) == 1


def test_unavailable_spell_excluded(monkeypatch):
    from mechanical_magic_spell_profiles import build_profile_battlefield_evidence
    available = assigned("AVAILABLE")
    hidden = assigned("HIDDEN")
    model = caster(spells=[available, hidden])
    # Model a rule-dependent availability decision without modifying production.
    monkeypatch.setattr(
        "mechanical_magic_spell_profiles.build_profile_battlefield_evidence",
        lambda profile: SimpleNamespace(available_spells=[available])
    )
    report = build_profile_magic_casting_evidence(model)
    assert [option.spell_id for option in report.spell_options] == ["AVAILABLE"]
    assert report.excluded_spell_ids == ("HIDDEN",)


def test_dg_rule_creates_conditional_option_without_free_will():
    report = build_profile_magic_casting_evidence(
        caster("DG_NEC", spells=[assigned()]),
        army=object(), army_list=rules("DG_HIS_SPIRIT")
    )
    assert len(report.spell_options) == 2
    baseline, conditional = report.spell_options
    assert baseline.conditional_rule_ids == ()
    assert conditional.conditional_rule_ids == ("DG_HIS_SPIRIT",)
    assert conditional.condition_verified is False
    assert conditional.allocations[0].probability == pytest.approx(8/9)
    assert conditional.allocations[0].will_spent == 1
    assert conditional.allocations[0].extra_dice_source == "DG_HIS_SPIRIT"


def test_same_rule_not_applied_to_unrelated_profile():
    report = build_profile_magic_casting_evidence(
        caster(spells=[assigned()]),
        army=object(), army_list=rules("DG_HIS_SPIRIT")
    )
    assert len(report.spell_options) == 1
    assert report.conditional_extra_casting_dice == 0


def test_extra_cast_rule_is_not_multiplied_into_allocations():
    report = build_profile_magic_casting_evidence(
        caster("DG_NEC", spells=[assigned()]),
        army=object(), army_list=rules("DG_POWER_OF_THE_NECROMANCER")
    )
    assert report.conditional_extra_casts_per_opportunity == 1
    assert report.conditional_extra_cast_sources == ("DG_POWER_OF_THE_NECROMANCER",)
    assert len(report.spell_options) == 1
    assert len(report.spell_options[0].allocations) == 3


@pytest.mark.parametrize("remaining", [-1, 2.5, True])
def test_bad_remaining_will_rejected(remaining):
    with pytest.raises((ValueError, TypeError)):
        build_profile_magic_casting_evidence(caster(), remaining_will=remaining)


def test_army_and_army_list_must_be_paired():
    with pytest.raises(ValueError, match="together"):
        build_profile_magic_casting_evidence(caster(), army_list=rules())


def test_unsupported_profile_type_rejected():
    with pytest.raises(TypeError, match="profile"):
        build_profile_magic_casting_evidence(object())


def test_no_rules_does_not_create_conditional_casts():
    report = build_profile_magic_casting_evidence(
        caster("DG_NEC", spells=[assigned()]),
        army=object(), army_list=rules()
    )
    assert len(report.spell_options) == 1


def test_multiple_spells_do_not_imply_cast_frequency():
    report = build_profile_magic_casting_evidence(
        caster(spells=[assigned("A", 3), assigned("B", 4)])
    )
    assert len(report.spell_options) == 2
    assert not hasattr(report, "expected_casts_per_turn")
    assert all(not opt.condition_verified for opt in report.spell_options)

"""DEV-078-ROTN-C2: existing spell evidence -> cast sequence integration."""
from types import SimpleNamespace
import pytest

from necromancer_cast_sequence import CastDeclaration
from necromancer_magic_sequence_adapter import assess_declared_cast_sequence


def evidence(profile="DG_NEC", *spell_ids):
    return SimpleNamespace(
        profile_id=profile,
        spell_options=tuple(SimpleNamespace(spell_id=s) for s in spell_ids),
    )


def army_list(list_id="DG_ROTN", rule=True):
    return SimpleNamespace(
        id=list_id,
        army_rules=[SimpleNamespace(id="DG_POWER_OF_THE_NECROMANCER")] if rule else [],
    )


def cast(spell, target=None, enemy=False):
    return CastDeclaration(spell, target, enemy)


def assess(declarations, *, profile="DG_NEC", list_id="DG_ROTN", rule=True):
    return assess_declared_cast_sequence(
        evidence(profile, "TRANSFIX", "SAP_WILL"),
        tuple(declarations), army_list=army_list(list_id, rule),
    )


def test_two_distinct_spells_allowed_with_army_rule():
    report = assess([cast("TRANSFIX", "a", True), cast("SAP_WILL", "b", True)])
    assert report.validated
    assert report.cast_attempts == report.permitted_cast_attempts == 2
    assert report.dashboard_score is None and report.scenario_score is None


def test_duplicate_spell_rejected():
    with pytest.raises(ValueError, match="same power"):
        assess([cast("TRANSFIX"), cast("TRANSFIX")])


def test_duplicate_enemy_rejected():
    with pytest.raises(ValueError, match="same enemy"):
        assess([cast("TRANSFIX", "a", True), cast("SAP_WILL", "a", True)])


def test_not_registered_rejected_as_single_cast():
    with pytest.raises(ValueError, match="activation limit"):
        assess([cast("TRANSFIX"), cast("SAP_WILL")], rule=False)


def test_other_army_cannot_enable_power():
    with pytest.raises(ValueError, match="activation limit"):
        assess([cast("TRANSFIX"), cast("SAP_WILL")], list_id="DG_PITS")


def test_other_profile_cannot_enable_power():
    with pytest.raises(ValueError, match="activation limit"):
        assess([cast("TRANSFIX"), cast("SAP_WILL")], profile="DG_KHM")


def test_unavailable_spell_rejected():
    with pytest.raises(ValueError, match="available repertoire"):
        assess([cast("UNAVAILABLE")])


def test_conditional_dice_option_does_not_inflate_spell_count():
    report = assess_declared_cast_sequence(
        evidence("DG_NEC", "TRANSFIX", "TRANSFIX", "SAP_WILL"),
        (cast("TRANSFIX"), cast("SAP_WILL")), army_list=army_list(),
    )
    assert report.cast_attempts == 2


def test_no_target_inferred():
    assert assess([cast("TRANSFIX"), cast("SAP_WILL")]).validated


def test_invalid_evidence_rejected():
    with pytest.raises(TypeError, match="spell_options"):
        assess_declared_cast_sequence(SimpleNamespace(profile_id="DG_NEC"), (), army_list=army_list())

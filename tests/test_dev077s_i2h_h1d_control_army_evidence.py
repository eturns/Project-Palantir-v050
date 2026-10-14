"""DEV-077S-I2-H1-D: conditional roster and spend evidence regression."""
from dataclasses import dataclass
import pytest
from control_army_evidence import (
    ControlCheck, DeclaredControlCast, evaluate_army_control_contract,
)


@dataclass(frozen=True)
class Group:
    profile_id: str
    quantity: int
    initial_will_per_model: int
    available_spell_ids: tuple[str, ...]


@dataclass(frozen=True)
class Category:
    tag_id: str
    distinct_spell_ids: tuple[str, ...]


@dataclass(frozen=True)
class Contract:
    caster_groups: tuple[Group, ...]
    effect_categories: tuple[Category, ...]


@pytest.fixture
def roster():
    return Contract(
        (Group("DG_NEC", 1, 20, ("TRANSFIX", "COMPEL", "CURSE")),
         Group("DG_NAZ", 2, 1, ()), Group("TEST_MAGE", 1, 2, ("TRANSFIX",))),
        (Category("CONTROL", ("TRANSFIX", "COMPEL")),
         Category("HERO_HUNTING", ("CURSE",))),
    )


def cast(*, event="cast-1", caster="DG_NEC#1", spell="TRANSFIX", turn=1,
         spent=1, available=ControlCheck.VERIFIED_TRUE,
         target=ControlCheck.VERIFIED_TRUE,
         success=ControlCheck.VERIFIED_TRUE):
    return DeclaredControlCast(event, turn, caster, "ENEMY#1", spell, spent,
                               available, target, success)


def test_necromancer_and_second_caster_from_roster(roster):
    result = evaluate_army_control_contract(roster)
    assert result.control_caster_count == 2
    assert result.starting_control_caster_will == 22
    assert result.distinct_control_spell_ids == ("COMPEL", "TRANSFIX")
    assert tuple(c.model_id for c in result.casters) == ("DG_NEC#1", "TEST_MAGE#1")


def test_spell_ownership_does_not_create_declared_casts(roster):
    result = evaluate_army_control_contract(roster)
    assert result.evaluated_casts == () and result.declared_will_spent == 0
    assert result.dashboard_score is None and result.scenario_score is None


def test_verified_transfix_is_only_candidate_not_applied(roster):
    result = evaluate_army_control_contract(roster, (cast(),))
    assert result.evaluated_casts[0].eligible_for_effect_application
    assert result.evaluated_casts[0].result == "verified_candidate_for_h1b"
    assert result.cross_method_resource_reconciliation == "not_verified"


@pytest.mark.parametrize("field", ["available", "target", "success"])
def test_unknown_evidence_never_automatically_applies(roster, field):
    args = {field: ControlCheck.UNKNOWN}
    item = evaluate_army_control_contract(roster, (cast(**args),)).evaluated_casts[0]
    assert item.result == "unresolved" and not item.eligible_for_effect_application


@pytest.mark.parametrize("field", ["available", "target", "success"])
def test_explicit_negative_evidence_blocks_application(roster, field):
    item = evaluate_army_control_contract(
        roster, (cast(**{field: ControlCheck.VERIFIED_FALSE}),)
    ).evaluated_casts[0]
    assert item.result == "verified_not_applied"


def test_unlisted_spell_is_rejected(roster):
    with pytest.raises(ValueError, match="does not have"):
        evaluate_army_control_contract(roster, (cast(spell="CURSE"),))


def test_unknown_caster_is_rejected(roster):
    with pytest.raises(ValueError, match="unknown"):
        evaluate_army_control_contract(roster, (cast(caster="DG_NAZ#1"),))


def test_duplicate_event_rejected(roster):
    with pytest.raises(ValueError, match="duplicate"):
        evaluate_army_control_contract(roster, (cast(), cast()))


def test_second_cast_same_turn_not_inferred(roster):
    with pytest.raises(ValueError, match="multiple casts"):
        evaluate_army_control_contract(roster, (cast(), cast(event="cast-2", spell="COMPEL")))


def test_casts_different_turns_and_will_total(roster):
    result = evaluate_army_control_contract(roster, (cast(), cast(event="cast-2", turn=2, spent=2)))
    assert result.declared_will_spent == 3
    assert len(result.evaluated_casts) == 2


def test_cast_will_cannot_exceed_personal_pool(roster):
    with pytest.raises(ValueError, match="exceed"):
        evaluate_army_control_contract(roster, (cast(spent=21),))


def test_will_cannot_be_transferred_between_casters(roster):
    with pytest.raises(ValueError, match="exceed"):
        evaluate_army_control_contract(roster, (cast(caster="TEST_MAGE#1", spent=3),))


def test_zero_will_caster_has_no_assumed_casts(roster):
    updated = Contract((Group("DG_NEC", 1, 0, ("TRANSFIX",)),), roster.effect_categories)
    assert evaluate_army_control_contract(updated).control_caster_count == 1
    with pytest.raises(ValueError, match="exceed"):
        evaluate_army_control_contract(updated, (cast(),))


@pytest.mark.parametrize("bad", [0, -1, True, 1.5])
def test_invalid_will_amount_rejected(bad):
    with pytest.raises(ValueError, match="will_spent"):
        cast(spent=bad)


def test_invalid_verdict_rejected():
    with pytest.raises(TypeError, match="opportunity_legal"):
        cast(available=True)


def test_non_control_categories_not_independently_counted(roster):
    result = evaluate_army_control_contract(roster)
    assert "CURSE" not in result.distinct_control_spell_ids


def test_multiple_same_profile_models_get_distinct_ids(roster):
    updated = Contract((Group("TEST_MAGE", 2, 2, ("TRANSFIX",)),), roster.effect_categories)
    result = evaluate_army_control_contract(updated)
    assert tuple(c.model_id for c in result.casters) == ("TEST_MAGE#1", "TEST_MAGE#2")


def test_zero_qty_rejected(roster):
    updated = Contract((Group("DG_NEC", 0, 20, ("TRANSFIX",)),), roster.effect_categories)
    with pytest.raises(ValueError, match="quantity"):
        evaluate_army_control_contract(updated)

"""GT-C3B1 focused Immobile and Heavy Object tests."""
from types import SimpleNamespace
import pytest
from goblin_scribe_immobile import (
    ScribeCarryingContext, assess_scribe_immobile, assess_scribe_carrying
)

def make_model(profile_id="GT_SCRIBE", rule=True):
    rules=(SimpleNamespace(rule=SimpleNamespace(id="IMMOBILE")),) if rule else ()
    return SimpleNamespace(
        profile=SimpleNamespace(id=profile_id),
        effective_special_rules=rules,
    )

def context(**changes):
    values=dict(carrier_is_friendly=True,
                carrying_allowed_by_heavy_object_rules=True,
                carrier_finished_move=False)
    values.update(changes)
    return ScribeCarryingContext(**values)

def test_immobile_rule_contract():
    result=assess_scribe_immobile(make_model())
    assert result.immobile_rule_active
    assert result.may_move_independently is False
    assert result.counts_as_trapped_if_duel_lost is True
    assert result.may_be_carried_as_heavy_object is True
    assert result.must_be_put_down_after_carrier_move
    assert result.may_be_carried_onto_board

def test_unrelated_character_not_affected():
    assert assess_scribe_immobile(make_model("GT_GRINNAH")) is None

def test_missing_rule_fails_closed():
    with pytest.raises(ValueError,match="IMMOBILE"):
        assess_scribe_immobile(make_model(rule=False))

def test_legal_carrying():
    evidence=assess_scribe_carrying(make_model(),context())
    assert evidence.can_carry
    assert not evidence.must_put_down_now

def test_carrier_finishing_move_requires_put_down():
    evidence=assess_scribe_carrying(make_model(),context(carrier_finished_move=True))
    assert evidence.can_carry
    assert evidence.must_put_down_now

def test_can_arrive_by_carrier_when_scenario_allows():
    evidence=assess_scribe_carrying(make_model(),context(entering_board_via_scenario=True))
    assert evidence.entering_board_by_carrier_permitted

@pytest.mark.parametrize("changes",[
    {"carrier_is_friendly":False},
    {"carrying_allowed_by_heavy_object_rules":False},
])
def test_carrying_requires_eligible_carrier(changes):
    evidence=assess_scribe_carrying(make_model(),context(**changes))
    assert evidence.can_carry is False
    assert evidence.must_put_down_now is False

def test_unrelated_model_cannot_use_scribe_carrying():
    evidence=assess_scribe_carrying(make_model("GT_WARRIOR"),context())
    assert not evidence.can_carry

@pytest.mark.parametrize("changes",[
    {"carrier_is_friendly":None},
    {"carrying_allowed_by_heavy_object_rules":1},
    {"carrier_finished_move":"yes"},
    {"entering_board_via_scenario":None},
])
def test_reject_non_boolean_context(changes):
    with pytest.raises(TypeError):
        context(**changes)

def test_requires_valid_context_object():
    with pytest.raises(TypeError):
        assess_scribe_carrying(make_model(),None)

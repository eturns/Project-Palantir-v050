"""DEV-077S-I2-H2-A: permissions, resources and conservative evidence."""
import pytest
from command_action_declaration import (
    CommandActionDeclaration, CommandCheck, CommandDecision,
    evaluate_command_declaration,
)
from hero_resource_state import HeroResourceState

KNOWN = ("HEROIC_MOVE", "HEROIC_MARCH", "HEROIC_STRIKE")
AVAILABLE = ("HEROIC_MOVE", "HEROIC_MARCH")
TRUE = CommandCheck.VERIFIED_TRUE
FALSE = CommandCheck.VERIFIED_FALSE
UNKNOWN = CommandCheck.UNKNOWN


def declaration(**overrides):
    args = dict(event_id="c1", actor_id="DG_HOC#1",
                heroic_action_id="HEROIC_MOVE", turn=1,
                timing_legal=TRUE, activation_legal=TRUE,
                battlefield_legal=TRUE)
    args.update(overrides)
    return CommandActionDeclaration(**args)


def evaluate(d=None, might=2, **kwargs):
    return evaluate_command_declaration(
        d or declaration(), known_action_ids=kwargs.get("known_action_ids", KNOWN),
        available_action_ids=kwargs.get("available_action_ids", AVAILABLE),
        resources=HeroResourceState(remaining_might=might, remaining_will=3, remaining_fate=1),
    )


def test_permitted_declaration_spends_might_once():
    e = evaluate()
    assert e.decision is CommandDecision.PERMITTED
    assert e.might_spent == 1 and e.remaining_resources.remaining_might == 1
    assert e.remaining_resources.remaining_will == 3
    assert e.effect_resolved is False


def test_unavailable_action_rejected():
    e = evaluate(declaration(heroic_action_id="HEROIC_STRIKE"))
    assert e.decision is CommandDecision.FORBIDDEN and e.might_spent == 0


def test_unknown_catalogue_action_rejected():
    assert evaluate(declaration(heroic_action_id="NOT_A_HEROIC_ACTION")).reason == "unknown_action"


@pytest.mark.parametrize("field", ["timing_legal", "activation_legal", "battlefield_legal"])
def test_missing_evidence_is_unresolved_without_spend(field):
    e = evaluate(declaration(**{field: UNKNOWN}))
    assert e.decision is CommandDecision.UNRESOLVED
    assert e.might_spent == 0


@pytest.mark.parametrize("field", ["timing_legal", "activation_legal", "battlefield_legal"])
def test_explicit_illegality_is_forbidden(field):
    assert evaluate(declaration(**{field: FALSE})).decision is CommandDecision.FORBIDDEN


def test_no_might_cannot_declare_paid_action():
    e = evaluate(might=0)
    assert e.decision is CommandDecision.FORBIDDEN
    assert e.remaining_resources.remaining_might == 0


def test_unknown_and_false_is_forbidden():
    e = evaluate(declaration(timing_legal=UNKNOWN, battlefield_legal=FALSE))
    assert e.decision is CommandDecision.FORBIDDEN


def test_missing_or_invalid_state_is_rejected():
    with pytest.raises(TypeError):
        evaluate_command_declaration(declaration(), known_action_ids=KNOWN,
                                     available_action_ids=AVAILABLE, resources=None)


def test_invalid_turn_and_cost_rejected():
    with pytest.raises(ValueError):
        declaration(turn=0)
    with pytest.raises(ValueError):
        declaration(might_cost=-1)
    with pytest.raises(ValueError):
        declaration(might_cost=True)


def test_invalid_check_rejected():
    with pytest.raises(TypeError):
        declaration(timing_legal=True)


def test_catalogue_inconsistency_rejected():
    with pytest.raises(ValueError):
        evaluate(available_action_ids=("HEROIC_MOVE", "INVALID"))


def test_no_dashboard_score_or_effect_inference():
    e = evaluate()
    assert e.dashboard_score is None and e.scenario_score is None
    assert not e.effect_resolved

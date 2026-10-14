from fractions import Fraction
import pytest

from hero_resource_state import HeroResourceState
from hero_hunting_resource_adapter import (
    DeclaredMethodSpend, HeroHuntingMethod, reconcile_cross_method_resources,
)
from hero_hunting_evidence_consistency import (
    EvidenceStatus, OutcomeType, MethodEvidence, check_hero_hunting_evidence,
)


def ledger():
    return reconcile_cross_method_resources(
        {"caster": HeroResourceState(1, 2, 1)},
        (DeclaredMethodSpend("caster", HeroHuntingMethod.MAGIC_CAST, will=1),),
    )


def item(eid="e1", event="cast1", outcome=OutcomeType.ELIMINATION,
         status=EvidenceStatus.VERIFIED, chance=Fraction(1, 3), actor="caster",
         target="hero", method=HeroHuntingMethod.MAGIC_CAST):
    return MethodEvidence(eid, event, actor, target, method, outcome,
                          status, chance, "MESBG Rules Manual (2024)")


def test_verified_evidence_admitted_but_not_scored():
    result = check_hero_hunting_evidence((item(),), ledger())
    assert result.verified_count == 1
    assert result.elimination_probability is None
    assert result.dashboard_score is None
    assert result.scenario_score is None


def test_separate_outcome_types_not_conflated():
    result = check_hero_hunting_evidence((
        item(), item("e2", "cast1", OutcomeType.CONTROL),
        item("e3", "cast1", OutcomeType.RESOURCE_DEPLETION),
    ), ledger())
    assert {e.outcome for e in result.observations} == set(OutcomeType)


def test_no_naive_summation_of_different_events_on_same_target():
    result = check_hero_hunting_evidence((item(), item("e2", "cast2")), ledger())
    assert len(result.observations) == 2
    assert result.elimination_probability is None


def test_duplicate_evidence_id_rejected():
    with pytest.raises(ValueError, match="Duplicate evidence_id"):
        check_hero_hunting_evidence((item(), item()), ledger())


def test_same_event_outcome_cannot_be_relabelled_and_counted_twice():
    with pytest.raises(ValueError, match="Duplicate event/outcome"):
        check_hero_hunting_evidence((item(), item("e2")), ledger())


def test_unknown_actor_rejected():
    with pytest.raises(ValueError, match="Unknown acting model"):
        check_hero_hunting_evidence((item(actor="unknown"),), ledger())


@pytest.mark.parametrize("status", [EvidenceStatus.UNSUPPORTED, EvidenceStatus.UNRESOLVED])
def test_unresolved_observation_has_no_numeric_probability(status):
    result = check_hero_hunting_evidence((item(status=status, chance=None),), ledger())
    assert result.unresolved_count == 1
    assert result.observations[0].probability is None


@pytest.mark.parametrize("status", [EvidenceStatus.UNSUPPORTED, EvidenceStatus.UNRESOLVED])
def test_unresolved_cannot_smuggle_in_probability(status):
    with pytest.raises(ValueError, match="cannot declare probability"):
        item(status=status)


def test_verified_missing_probability_rejected():
    with pytest.raises(ValueError, match="requires a probability"):
        item(chance=None)


def test_verified_missing_rule_source_rejected():
    with pytest.raises(ValueError, match="rule_source"):
        MethodEvidence("id", "event", "caster", "target", HeroHuntingMethod.MELEE,
                       OutcomeType.ELIMINATION, EvidenceStatus.VERIFIED, Fraction(1,2))


@pytest.mark.parametrize("chance", [Fraction(-1, 2), Fraction(3, 2)])
def test_invalid_probability_rejected(chance):
    with pytest.raises(ValueError, match="between zero and one"):
        item(chance=chance)


def test_float_probability_rejected():
    with pytest.raises(TypeError, match="Fraction"):
        item(chance=0.5)


def test_missing_resource_ledger_rejected():
    with pytest.raises(TypeError, match="CrossMethodResources"):
        check_hero_hunting_evidence((item(),), None)


def test_empty_evidence_is_valid_and_not_scored():
    result = check_hero_hunting_evidence((), ledger())
    assert result.verified_count == 0
    assert result.elimination_probability is None


def test_input_requires_tuple():
    with pytest.raises(TypeError, match="tuple"):
        check_hero_hunting_evidence([item()], ledger())


def test_cross_method_budget_remains_checked():
    with pytest.raises(ValueError, match="Will exceeds"):
        reconcile_cross_method_resources(
            {"caster": HeroResourceState(0, 1, 0)},
            (DeclaredMethodSpend("caster", HeroHuntingMethod.MAGIC_CAST, will=1),
             DeclaredMethodSpend("caster", HeroHuntingMethod.MAGIC_RESIST, will=1)),
        )

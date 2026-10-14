"""H2-C standalone command coverage tests (no inferred distances or scores)."""
import pytest
from command_coverage import (
    CommandCoverageObservation, CommandCoverageStatus,
    CommandVerification as V, aggregate_command_coverage,
    classify_command_observation,
)


def observation(**changes):
    data = dict(command_id="MOVE#1", provider_id="HERO#1", recipient_id="ORC#1",
                benefit_id="move_priority", turn=1, provider_permission=V.VERIFIED_TRUE,
                recipient_eligible=V.VERIFIED_TRUE,
                within_required_range=V.VERIFIED_TRUE,
                timing_permitted=V.VERIFIED_TRUE)
    data.update(changes)
    return CommandCoverageObservation(**data)


def test_verified_coverage():
    r = aggregate_command_coverage((observation(),))
    assert r.distinct_verified_model_turn_benefits == 1
    assert r.dashboard_score is None and r.scenario_score is None


@pytest.mark.parametrize("field", ["provider_permission", "recipient_eligible",
                                     "within_required_range", "timing_permitted"])
def test_failed_gate_excludes_recipient(field):
    x = observation(**{field: V.VERIFIED_FALSE})
    assert classify_command_observation(x) is CommandCoverageStatus.INELIGIBLE
    assert aggregate_command_coverage((x,)).distinct_verified_model_turn_benefits == 0


@pytest.mark.parametrize("field", ["provider_permission", "recipient_eligible",
                                     "within_required_range", "timing_permitted"])
def test_missing_evidence_is_unresolved(field):
    x = observation(**{field: V.UNKNOWN})
    result = aggregate_command_coverage((x,))
    assert len(result.unresolved_keys) == 1
    assert result.distinct_verified_model_turn_benefits == 0


def test_negative_overrides_unknown():
    assert classify_command_observation(observation(
        within_required_range=V.UNKNOWN, recipient_eligible=V.VERIFIED_FALSE
    )) is CommandCoverageStatus.INELIGIBLE


def test_overlap_same_benefit_same_turn_deduplicated():
    r = aggregate_command_coverage((observation(), observation(command_id="MOVE#2", provider_id="HERO#2")))
    assert r.distinct_verified_model_turn_benefits == 1
    assert r.overlap_count == 1


def test_distinct_benefit_counts_separately():
    r = aggregate_command_coverage((observation(), observation(command_id="MARCH#1", benefit_id="march")))
    assert r.distinct_verified_model_turn_benefits == 2


def test_different_turns_are_distinct():
    r = aggregate_command_coverage((observation(), observation(turn=2)))
    assert r.distinct_verified_model_turn_benefits == 2


def test_unresolved_overlap_does_not_add_verified():
    r = aggregate_command_coverage((observation(), observation(
        command_id="MOVE#2", provider_id="HERO#2", within_required_range=V.UNKNOWN
    )))
    assert r.distinct_verified_model_turn_benefits == 1
    assert not r.unresolved_keys


def test_duplicate_observation_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        aggregate_command_coverage((observation(), observation()))


@pytest.mark.parametrize("field,value", [("turn", 0), ("turn", True), ("command_id", " ")])
def test_invalid_identity_rejected(field, value):
    with pytest.raises(ValueError):
        observation(**{field: value})


def test_invalid_verification_rejected():
    with pytest.raises(TypeError):
        observation(timing_permitted=True)


def test_invalid_collection_rejected():
    with pytest.raises(TypeError):
        aggregate_command_coverage([observation()])


def test_empty_collection():
    assert aggregate_command_coverage(()).distinct_verified_model_turn_benefits == 0

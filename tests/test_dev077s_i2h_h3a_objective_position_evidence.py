"""DEV-077S-I2-H3-A objective snapshot evidence tests."""
from dataclasses import FrozenInstanceError
from fractions import Fraction as F

import pytest

from objective_position_evidence import (
    ObjectiveLocation, ObjectiveModelPosition, ObjectivePresenceStatus,
    ObjectiveVerification as V, assess_objective_positions,
)


def objective(radius=3):
    return ObjectiveLocation("obj", F(0), F(0), F(radius))


def model(name, army, x=0, y=0, eligible=V.TRUE, weight=1):
    return ObjectiveModelPosition(
        name, army, None if x is None else F(x),
        None if y is None else F(y), eligible, weight,
    )


def test_single_verified_model_leads():
    report = assess_objective_positions(objective(), (model("a", "good"),))
    assert report.controlling_army_id == "good"
    assert report.verified_presence_by_army == (("good", 1),)
    assert report.scenario_score is None and report.dashboard_score is None


def test_outside_radius_does_not_contribute():
    report = assess_objective_positions(objective(), (model("a", "good", 4),))
    assert report.status == "unoccupied"
    assert report.model_evidence[0].position_status is ObjectivePresenceStatus.OUTSIDE_RANGE


def test_radius_boundary_is_included():
    report = assess_objective_positions(objective(5), (model("a", "good", 3, 4),))
    assert report.controlling_army_id == "good"


def test_equal_presence_is_contested():
    report = assess_objective_positions(objective(),
                                        (model("a", "good"), model("b", "evil")))
    assert report.controlling_army_id is None
    assert report.status == "contested_equal_presence"


def test_higher_verified_presence_leads():
    report = assess_objective_positions(objective(),
                                        (model("a", "good", weight=2), model("b", "evil")))
    assert report.controlling_army_id == "good"


def test_unknown_position_preserves_uncertainty():
    report = assess_objective_positions(objective(),
                                        (model("a", "good"), model("b", "evil", None, None)))
    assert report.controlling_army_id is None
    assert report.unresolved_model_count == 1


def test_unknown_eligibility_preserves_uncertainty():
    report = assess_objective_positions(objective(),
                                        (model("a", "good"), model("b", "evil", eligible=V.UNKNOWN)))
    assert report.status == "unresolved_competing_evidence"


def test_verified_ineligible_model_does_not_count():
    report = assess_objective_positions(objective(),
                                        (model("a", "good", eligible=V.FALSE),))
    assert report.status == "unoccupied"


def test_distant_unknown_eligibility_cannot_contest():
    report = assess_objective_positions(objective(),
                                        (model("a", "good"), model("b", "evil", 20, eligible=V.UNKNOWN)))
    assert report.controlling_army_id == "good"


def test_duplicate_model_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        assess_objective_positions(objective(), (model("a", "good"), model("a", "evil")))


def test_invalid_partial_coordinates_rejected():
    with pytest.raises(ValueError, match="both"):
        ObjectiveModelPosition("m", "a", F(0), None, V.TRUE)


@pytest.mark.parametrize("weight", (0, -1, True, 1.0))
def test_invalid_presence_weight_rejected(weight):
    with pytest.raises(ValueError):
        model("m", "a", weight=weight)


def test_invalid_coordinate_type_rejected():
    with pytest.raises(TypeError):
        ObjectiveLocation("a", 0, F(0), F(3))


def test_invalid_verification_rejected():
    with pytest.raises(TypeError):
        model("a", "good", eligible=True)


def test_snapshot_objects_immutable():
    instance = objective()
    with pytest.raises(FrozenInstanceError):
        instance.objective_id = "changed"


def test_empty_snapshot_is_unoccupied():
    assert assess_objective_positions(objective(), ()).status == "unoccupied"

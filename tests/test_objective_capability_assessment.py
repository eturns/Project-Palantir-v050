from analysis_constants import (
    EXCEPTIONAL,
    WEAK,
)
from objective_capability_assessment import (
    ObjectiveCapabilityAssessment,
    assess_objective_contribution,
)
from objective_score import ObjectiveContribution


def test_assess_objective_contribution_preserves_name_and_value():
    contribution = ObjectiveContribution(
        name="magic",
        value=0.31,
    )

    assessment = assess_objective_contribution(
        contribution,
    )

    assert assessment.name == "magic"
    assert assessment.value == 0.31


def test_assess_objective_contribution_classifies_weak_capability():
    contribution = ObjectiveContribution(
        name="magic",
        value=0.31,
    )

    assessment = assess_objective_contribution(
        contribution,
    )

    assert assessment.rating == WEAK


def test_assess_objective_contribution_classifies_exceptional_capability():
    contribution = ObjectiveContribution(
        name="combat_capability",
        value=0.83,
    )

    assessment = assess_objective_contribution(
        contribution,
    )

    assert assessment == ObjectiveCapabilityAssessment(
        name="combat_capability",
        value=0.83,
        rating=EXCEPTIONAL,
    )


def test_objective_capability_assessment_is_immutable():
    assessment = ObjectiveCapabilityAssessment(
        name="magic",
        value=0.31,
        rating=WEAK,
    )

    try:
        assessment.value = 0.50
    except Exception:
        pass

    assert assessment.value == 0.31
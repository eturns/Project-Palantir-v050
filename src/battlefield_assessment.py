from battlefield_assessment_entity import (
    BattlefieldAssessmentEntity,
)

from analysis_constants import (
    STRONG,
    EXCEPTIONAL,
    WEAK,
    VERY_WEAK,
)

def assess_battlefield(
    assessments,
) -> BattlefieldAssessmentEntity:
    """
    Determines an army's battlefield strengths
    and weaknesses.
    """

    strengths = []
    weaknesses = []

    for assessment in assessments:

        if assessment.rating in (
            STRONG,
            EXCEPTIONAL,
        ):
            strengths.append(
                assessment,
            )

        elif assessment.rating in (
            WEAK,
            VERY_WEAK,
        ):
            weaknesses.append(
                assessment,
            )

    return BattlefieldAssessmentEntity(
        strengths=strengths,
        weaknesses=weaknesses,
    )
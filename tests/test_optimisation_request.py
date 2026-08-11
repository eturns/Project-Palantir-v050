from optimisation_request import (
    OptimisationGoal,
    OptimisationRequest,
)
from composition_spec import (
    CompositionSelectionGroup,
    CompositionSpec,
)


def test_optimisation_request_stores_army_points_and_multiple_goals():
    request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.BOARD_PRESENCE,
            OptimisationGoal.MAGIC,
        ),
    )

    assert request.army == "Dol Guldur"
    assert request.points_limit == 700

    assert request.goals == (
        OptimisationGoal.BOARD_PRESENCE,
        OptimisationGoal.MAGIC,
    )

def test_optimisation_request_stores_optional_composition_spec():
    spec = CompositionSpec(
        fixed_profiles=(
            ("DG_NEC", 1),
        ),
        selection_groups=(
            CompositionSelectionGroup(
                profile_ids=(
                    "DG_WK",
                    "DG_KHM",
                ),
                selection_size=1,
            ),
        ),
    )

    request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.BALANCED,
        ),
        composition_spec=spec,
    )

    assert request.composition_spec is spec
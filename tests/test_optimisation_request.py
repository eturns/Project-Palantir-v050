from army_list import ArmyList
from faction import Faction
from optimisation_request import (
    OptimisationGoal,
    OptimisationRequest,
)
from composition_spec import (
    CompositionSelectionGroup,
    CompositionSpec,
)


def create_army_list() -> ArmyList:
    faction = Faction(
        id="DG",
        name="Dol Guldur",
    )

    return ArmyList(
        id="DG_ROTN",
        name="Rise of the Necromancer",
        faction=faction,
    )


def test_optimisation_request_stores_army_list_points_and_multiple_goals():
    army_list = create_army_list()

    request = OptimisationRequest(
        army_list=army_list,
        points_limit=700,
        goals=(
            OptimisationGoal.BOARD_PRESENCE,
            OptimisationGoal.MAGIC,
        ),
    )

    assert request.army_list is army_list
    assert request.points_limit == 700

    assert request.goals == (
        OptimisationGoal.BOARD_PRESENCE,
        OptimisationGoal.MAGIC,
    )


def test_optimisation_request_stores_optional_composition_spec():
    army_list = create_army_list()

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
        army_list=army_list,
        points_limit=700,
        goals=(
            OptimisationGoal.BALANCED,
        ),
        composition_spec=spec,
    )

    assert request.composition_spec is spec


def test_optimisation_goal_includes_scenario():
    assert OptimisationGoal.SCENARIO.value == "scenario"
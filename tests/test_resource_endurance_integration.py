from army import Army
from battle_length_assumption import BattleHorizon
from optimiser_candidate import OptimiserCandidate
from profiles import Profile
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)
from resource_endurance_objective import (
    ResourceEnduranceObjective,
)
from resource_strategy import ResourceStrategy


def create_profile(
    profile_id: str,
    *,
    might: int,
    will: int,
    fate: int,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=might,
        will=will,
        fate=fate,
        max_in_army=99,
    )


def test_balanced_resource_strategy_scores_higher_than_aggressive_for_same_army():
    hero = create_profile(
        "HERO",
        might=6,
        will=6,
        fate=6,
    )

    army = Army()
    army.add_profile(
        hero,
        quantity=1,
    )

    balanced_objective = ResourceEnduranceObjective(
        assumption=ResourceEnduranceAssumption(
            horizon=BattleHorizon.SHORT,
            strategy=ResourceStrategy.BALANCED,
        ),
    )

    aggressive_objective = ResourceEnduranceObjective(
        assumption=ResourceEnduranceAssumption(
            horizon=BattleHorizon.SHORT,
            strategy=ResourceStrategy.AGGRESSIVE,
        ),
    )

    candidate = OptimiserCandidate(
        army=army,
    )

    balanced_score = balanced_objective.evaluate(
        candidate,
    )

    aggressive_score = aggressive_objective.evaluate(
        candidate,
    )

    assert balanced_score > aggressive_score
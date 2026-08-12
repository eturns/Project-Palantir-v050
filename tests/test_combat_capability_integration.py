from army import Army
from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from combat_capability_objective import (
    CombatCapabilityObjective,
)
from optimiser_candidate import OptimiserCandidate
from profiles import Profile


def create_profile(
    profile_id: str,
    *,
    fight: int,
    strength: int,
    defence: int,
    attacks: int,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=0,
        movement=6,
        fight=fight,
        shooting="4+",
        strength=strength,
        defence=defence,
        attacks=attacks,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=99,
    )


def test_combat_capability_objective_ranks_stronger_army_higher():
    weaker_profile = create_profile(
        "WEAKER",
        fight=3,
        strength=3,
        defence=4,
        attacks=1,
    )

    stronger_profile = create_profile(
        "STRONGER",
        fight=5,
        strength=6,
        defence=7,
        attacks=2,
    )

    weaker_army = Army()
    weaker_army.add_profile(
        weaker_profile,
        quantity=5,
    )

    stronger_army = Army()
    stronger_army.add_profile(
        stronger_profile,
        quantity=5,
    )

    objective = CombatCapabilityObjective(
        benchmark=DEFAULT_COMBAT_BENCHMARK,
    )

    weaker_score = objective.evaluate(
        OptimiserCandidate(
            army=weaker_army,
        )
    )

    stronger_score = objective.evaluate(
        OptimiserCandidate(
            army=stronger_army,
        )
    )

    assert stronger_score > weaker_score
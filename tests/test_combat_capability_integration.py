import pytest
from army import Army
from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from combat_benchmark_portfolio import (
    BALANCED_ALL_COMERS_V1,
)
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

def make_combat_profile(
    profile_id: str,
    fight: int,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=80,
        movement=6,
        fight=fight,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=2,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )


def test_f6_gains_value_over_f5_across_balanced_all_comers_portfolio():
    f5_army = Army()
    f6_army = Army()

    f5_army.add_profile(
        make_combat_profile(
            profile_id="F5_TEST",
            fight=5,
        )
    )

    f6_army.add_profile(
        make_combat_profile(
            profile_id="F6_TEST",
            fight=6,
        )
    )

    f5_candidate = OptimiserCandidate(
        army=f5_army,
    )

    f6_candidate = OptimiserCandidate(
        army=f6_army,
    )

    single_benchmark_objective = CombatCapabilityObjective(
        benchmark=DEFAULT_COMBAT_BENCHMARK,
    )

    portfolio_objective = CombatCapabilityObjective(
        benchmark=BALANCED_ALL_COMERS_V1,
    )

    f5_single_score = single_benchmark_objective.evaluate(
        f5_candidate,
    )

    f6_single_score = single_benchmark_objective.evaluate(
        f6_candidate,
    )

    f5_portfolio_score = portfolio_objective.evaluate(
        f5_candidate,
    )

    f6_portfolio_score = portfolio_objective.evaluate(
        f6_candidate,
    )

    assert f6_single_score == pytest.approx(
        f5_single_score,
    )

    assert f6_portfolio_score > f5_portfolio_score
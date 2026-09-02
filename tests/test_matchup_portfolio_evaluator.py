from army import Army
from combat_benchmark_profile_loader import (
    load_combat_benchmark_profiles,
)
from matchup_portfolio_evaluator import (
    calculate_matchup_portfolio_results,
)
from matchup_result import MatchupResult
from optimiser_candidate import OptimiserCandidate
from profiles import Profile


def test_calculates_one_matchup_result_per_benchmark_profile():
    attacker = Profile(
        id="ATTACKER",
        name="Attacker",
        points=50,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    army = Army()

    army.add_profile(
        attacker,
        quantity=1,
    )

    candidate = OptimiserCandidate(
        army=army,
    )

    benchmark_profiles = (
        load_combat_benchmark_profiles()
    )

    results = calculate_matchup_portfolio_results(
        candidate=candidate,
        target_profiles=benchmark_profiles,
    )

    assert len(results) == 10

    assert all(
        isinstance(result, MatchupResult)
        for result in results
    )

    assert {
        result.target_profile_id
        for result in results
    } == {
        profile.id
        for profile in benchmark_profiles
    }
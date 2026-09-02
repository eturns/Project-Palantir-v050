from army import Army
from matchup_evaluator import calculate_matchup_result
from optimiser_candidate import OptimiserCandidate
from profiles import Profile


def test_calculates_matchup_result_against_target_profile():
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

    target = Profile(
        id="TARGET",
        name="Target",
        points=50,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
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

    result = calculate_matchup_result(
        candidate=candidate,
        target_profile=target,
    )

    assert result.target_profile_id == "TARGET"
    assert result.target_profile_name == "Target"

    assert 0.0 <= result.score <= 1.0

def test_matchup_result_includes_offensive_and_defensive_scores():
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

    target = Profile(
        id="TARGET",
        name="Target",
        points=50,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
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

    result = calculate_matchup_result(
        candidate=candidate,
        target_profile=target,
    )

    assert result.offensive_score is not None
    assert result.defensive_score is not None

    assert 0.0 <= result.offensive_score <= 1.0
    assert 0.0 <= result.defensive_score <= 1.0

def test_matchup_score_is_equal_weighted_offence_and_defence():
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

    target = Profile(
        id="TARGET",
        name="Target",
        points=50,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
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

    result = calculate_matchup_result(
        candidate=candidate,
        target_profile=target,
    )

    expected_score = (
        result.offensive_score * 0.5
        + result.defensive_score * 0.5
    )

    assert result.score == expected_score
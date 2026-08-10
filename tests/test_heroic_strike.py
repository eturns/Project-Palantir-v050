from heroic_strike import (
    HeroicStrike,
    apply_heroic_strike,
    generate_heroic_strike_outcomes,
    generate_fight_outcomes,
    generate_duel_fight_outcomes,
)


def test_heroic_strike_defaults_to_inactive():
    strike = HeroicStrike()

    assert strike.active is False


def test_heroic_strike_can_be_active():
    strike = HeroicStrike(active=True)

    assert strike.active is True

def test_apply_heroic_strike_increases_fight():
    result = apply_heroic_strike(
        base_fight=5,
        strike_roll=2,
    )

    assert result == 7

def test_apply_heroic_strike_caps_fight_at_ten():
    result = apply_heroic_strike(
        base_fight=9,
        strike_roll=3,
    )

    assert result == 10


def test_apply_heroic_strike_rejects_invalid_base_fight():
    try:
        apply_heroic_strike(
            base_fight=0,
            strike_roll=2,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for invalid base Fight.")


def test_apply_heroic_strike_rejects_invalid_strike_roll():
    try:
        apply_heroic_strike(
            base_fight=5,
            strike_roll=4,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for invalid Strike roll.")

def test_generate_heroic_strike_outcomes_returns_three_results():
    outcomes = generate_heroic_strike_outcomes(
        base_fight=5,
    )

    assert len(outcomes) == 3


def test_generate_heroic_strike_outcomes_contains_each_d3_result():
    outcomes = generate_heroic_strike_outcomes(
        base_fight=5,
    )

    assert outcomes == (6, 7, 8)


def test_generate_heroic_strike_outcomes_preserves_fight_ten_cap():
    outcomes = generate_heroic_strike_outcomes(
        base_fight=9,
    )

    assert outcomes == (10, 10, 10)

def test_generate_fight_outcomes_without_heroic_strike():
    outcomes = generate_fight_outcomes(
        base_fight=5,
        heroic_strike_active=False,
    )

    assert outcomes == (5,)


def test_generate_fight_outcomes_with_heroic_strike():
    outcomes = generate_fight_outcomes(
        base_fight=5,
        heroic_strike_active=True,
    )

    assert outcomes == (6, 7, 8)


def test_generate_fight_outcomes_rejects_invalid_fight():
    try:
        generate_fight_outcomes(
            base_fight=11,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for invalid Fight value.")

def test_generate_duel_fight_outcomes_without_strikes():
    outcomes = generate_duel_fight_outcomes(
        attacker_base_fight=5,
        defender_base_fight=4,
    )

    assert outcomes == ((5, 4),)


def test_generate_duel_fight_outcomes_with_attacker_strike():
    outcomes = generate_duel_fight_outcomes(
        attacker_base_fight=5,
        defender_base_fight=4,
        attacker_heroic_strike_active=True,
    )

    assert outcomes == (
        (6, 4),
        (7, 4),
        (8, 4),
    )


def test_generate_duel_fight_outcomes_with_both_strikes():
    outcomes = generate_duel_fight_outcomes(
        attacker_base_fight=5,
        defender_base_fight=5,
        attacker_heroic_strike_active=True,
        defender_heroic_strike_active=True,
    )

    assert len(outcomes) == 9
    assert outcomes[0] == (6, 6)
    assert outcomes[-1] == (8, 8)
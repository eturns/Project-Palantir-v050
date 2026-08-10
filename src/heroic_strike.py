from dataclasses import dataclass


@dataclass(frozen=True)
class HeroicStrike:
    active: bool = False

def apply_heroic_strike(
    base_fight: int,
    strike_roll: int,
) -> int:
    """
    Applies a Heroic Strike D3 result to a Fight value,
    capped at Fight 10.
    """

    if not 1 <= base_fight <= 10:
        raise ValueError("Base Fight must be between 1 and 10.")

    if not 1 <= strike_roll <= 3:
        raise ValueError("Heroic Strike roll must be between 1 and 3.")

    return min(
        base_fight + strike_roll,
        10,
    )

def generate_heroic_strike_outcomes(
    base_fight: int,
) -> tuple[int, int, int]:
    """
    Generates the three equally likely final Fight values
    from a Heroic Strike D3 roll.
    """

    return tuple(
        apply_heroic_strike(
            base_fight=base_fight,
            strike_roll=strike_roll,
        )
        for strike_roll in range(1, 4)
    )

def generate_fight_outcomes(
    base_fight: int,
    heroic_strike_active: bool = False,
) -> tuple[int, ...]:
    """
    Returns all possible final Fight values.

    Without Heroic Strike, the base Fight value is returned once.
    With Heroic Strike, the three equally likely D3 outcomes are returned.
    """

    if not 1 <= base_fight <= 10:
        raise ValueError("Base Fight must be between 1 and 10.")

    if not heroic_strike_active:
        return (base_fight,)

    return generate_heroic_strike_outcomes(
        base_fight=base_fight,
    )

def generate_duel_fight_outcomes(
    attacker_base_fight: int,
    defender_base_fight: int,
    attacker_heroic_strike_active: bool = False,
    defender_heroic_strike_active: bool = False,
) -> tuple[tuple[int, int], ...]:
    """
    Generates every equally weighted attacker and defender
    Fight-value combination for the Duel.
    """

    attacker_outcomes = generate_fight_outcomes(
        base_fight=attacker_base_fight,
        heroic_strike_active=attacker_heroic_strike_active,
    )

    defender_outcomes = generate_fight_outcomes(
        base_fight=defender_base_fight,
        heroic_strike_active=defender_heroic_strike_active,
    )

    return tuple(
        (attacker_fight, defender_fight)
        for attacker_fight in attacker_outcomes
        for defender_fight in defender_outcomes
    )
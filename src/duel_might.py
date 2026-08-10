from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class DuelMight:
    available: int = 0

    def __post_init__(self) -> None:
        if self.available < 0:
            raise ValueError("Available Might cannot be negative.")

class DuelMightStrategy(Enum):
    NEVER = "never"
    MINIMUM_TO_WIN = "minimum_to_win"
    MINIMUM_TO_AVOID_LOSS = "minimum_to_avoid_loss"
    MAXIMISE_ROLL = "maximise_roll"

@dataclass(frozen=True)
class DuelMightResolution:
    attacker_final_roll: int
    defender_final_roll: int
    attacker_might_spent: int
    defender_might_spent: int

def calculate_might_needed(
    current_roll: int,
    target_roll: int,
) -> int:
    """
    Returns the Might required to increase one Duel die
    from the current value to the target value.
    """

    if not 1 <= current_roll <= 6:
        raise ValueError("Current Duel roll must be between 1 and 6.")

    if not 1 <= target_roll <= 6:
        raise ValueError("Target Duel roll must be between 1 and 6.")

    if target_roll <= current_roll:
        return 0

    return target_roll - current_roll

def apply_might_to_roll(
    current_roll: int,
    might_spent: int,
    might_available: int,
) -> int:
    """
    Applies Might to one Duel die and returns the modified roll.
    """

    if not 1 <= current_roll <= 6:
        raise ValueError("Current Duel roll must be between 1 and 6.")

    if might_spent < 0:
        raise ValueError("Might spent cannot be negative.")

    if might_available < 0:
        raise ValueError("Available Might cannot be negative.")

    if might_spent > might_available:
        raise ValueError("Cannot spend more Might than is available.")

    if current_roll + might_spent > 6:
        raise ValueError("A Duel roll cannot be increased above 6.")

    return current_roll + might_spent

def choose_might_spend(
    current_roll: int,
    might_available: int,
    strategy: DuelMightStrategy,
    opponent_roll: int | None = None,
) -> int:
    """
    Chooses how much Might to spend on one Duel die.
    """

    if not 1 <= current_roll <= 6:
        raise ValueError("Current Duel roll must be between 1 and 6.")

    if might_available < 0:
        raise ValueError("Available Might cannot be negative.")

    if opponent_roll is not None and not 1 <= opponent_roll <= 6:
        raise ValueError("Opponent Duel roll must be between 1 and 6.")

    if strategy is DuelMightStrategy.NEVER:
        return 0

    if strategy is DuelMightStrategy.MAXIMISE_ROLL:
        return min(
            might_available,
            6 - current_roll,
        )

    if strategy is DuelMightStrategy.MINIMUM_TO_WIN:
        if opponent_roll is None:
            raise ValueError(
                "Opponent roll is required for minimum-to-win strategy."
            )

        target_roll = opponent_roll + 1

        if target_roll > 6:
            return 0

        might_needed = calculate_might_needed(
            current_roll=current_roll,
            target_roll=target_roll,
        )

        if might_needed > might_available:
            return 0

        return might_needed

    if strategy is DuelMightStrategy.MINIMUM_TO_AVOID_LOSS:
        if opponent_roll is None:
            raise ValueError(
                "Opponent roll is required for minimum-to-avoid-loss strategy."
            )

        if current_roll >= opponent_roll:
            return 0

        might_needed = calculate_might_needed(
            current_roll=current_roll,
            target_roll=opponent_roll,
        )

        if might_needed > might_available:
            return 0

        return might_needed

    raise NotImplementedError(
        f"Might strategy not implemented: {strategy.value}"
    )

def resolve_might_modified_roll(
    current_roll: int,
    might_available: int,
    strategy: DuelMightStrategy,
    opponent_roll: int | None = None,
) -> tuple[int, int]:
    """
    Returns:
    - the final modified Duel roll;
    - the amount of Might spent.
    """

    might_spent = choose_might_spend(
        current_roll=current_roll,
        might_available=might_available,
        strategy=strategy,
        opponent_roll=opponent_roll,
    )

    final_roll = apply_might_to_roll(
        current_roll=current_roll,
        might_spent=might_spent,
        might_available=might_available,
    )

    return final_roll, might_spent

def resolve_duel_might(
    attacker_roll: int,
    attacker_might_available: int,
    attacker_strategy: DuelMightStrategy,
    defender_roll: int,
    defender_might_available: int,
    defender_strategy: DuelMightStrategy,
) -> DuelMightResolution:
    """
    Resolves Might spending for both sides using their
    selected strategies.
    """

    attacker_final_roll, attacker_might_spent = (
        resolve_might_modified_roll(
            current_roll=attacker_roll,
            opponent_roll=defender_roll,
            might_available=attacker_might_available,
            strategy=attacker_strategy,
        )
    )

    defender_final_roll, defender_might_spent = (
        resolve_might_modified_roll(
            current_roll=defender_roll,
            opponent_roll=attacker_final_roll,
            might_available=defender_might_available,
            strategy=defender_strategy,
        )
    )

    return DuelMightResolution(
        attacker_final_roll=attacker_final_roll,
        defender_final_roll=defender_final_roll,
        attacker_might_spent=attacker_might_spent,
        defender_might_spent=defender_might_spent,
    )
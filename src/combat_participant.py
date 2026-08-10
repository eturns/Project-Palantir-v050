"""
Project Palantír
================

File:
    combat_participant.py

Purpose:
    Represents one model participating in a combat.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-043 – Multi-model Combats
"""

# ============================================================================
# Imports
# ============================================================================

from dataclasses import dataclass

from profiles import Profile


# ============================================================================
# Classes
# ============================================================================

@dataclass(frozen=True)
class CombatParticipant:
    """
    Represents one model contributing to a combat.

    duel_dice:
        The number of Duel dice contributed by this participant.

    contributes_fight:
        Whether this participant's Fight value may be used when
        determining the highest Fight value on its side.

    can_make_strikes:
        Whether this participant may make Strikes if its side wins.
        Supporting models normally contribute Duel dice and Fight,
        but cannot make Strikes.
    """

    profile: Profile
    duel_dice: int
    contributes_fight: bool = True
    can_make_strikes: bool = True

    def __post_init__(self) -> None:
        if self.duel_dice < 0:
            raise ValueError("Participant Duel dice cannot be negative.")

        if (
            self.duel_dice == 0
            and not self.contributes_fight
            and not self.can_make_strikes
        ):
            raise ValueError(
                "A combat participant must contribute to the combat."
            )


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("combat participant module loaded successfully.")
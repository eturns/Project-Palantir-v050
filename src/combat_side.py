"""
Project Palantír
================

File:
    combat_side.py

Purpose:
    Represents one side in a multi-model combat.

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

from combat_participant import CombatParticipant

from duel_might import DuelMightStrategy

# ============================================================================
# Classes
# ============================================================================

@dataclass(frozen=True)
class CombatSide:
    """
    Represents all participants fighting on one side of a combat.
    """

    participants: tuple[CombatParticipant, ...]
    reroll_available: bool = False
    might_user: CombatParticipant | None = None
    might_available: int = 0
    might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER
    heroic_strike_user: CombatParticipant | None = None

    def __post_init__(self) -> None:
        if not self.participants:
            raise ValueError(
                "A combat side must contain at least one participant."
            )

        if self.total_duel_dice < 1:
            raise ValueError(
                "A combat side must contribute at least one Duel die."
            )

        if not any(
            participant.contributes_fight
            for participant in self.participants
        ):
            raise ValueError(
                "A combat side must have at least one Fight contributor."
            )

        if self.might_available < 0:
            raise ValueError(
                "Available side Might cannot be negative."
            )

        if (
            self.might_user is not None
            and self.might_user not in self.participants
        ):
            raise ValueError(
                "The Might user must be a participant on this combat side."
            )

        if self.might_available > 0 and self.might_user is None:
            raise ValueError(
                "A combat side with available Might must identify its user."
            )

        if (
            self.might_user is not None
            and self.might_available > self.might_user.profile.might
        ):
            raise ValueError(
                "Available side Might cannot exceed the user's Might."
            )

        if (
            self.heroic_strike_user is not None
            and self.heroic_strike_user not in self.participants
        ):
            raise ValueError(
                "The Heroic Strike user must be a participant "
                "on this combat side."
            )

        if (
            self.heroic_strike_user is not None
            and not self.heroic_strike_user.contributes_fight
        ):
            raise ValueError(
                "The Heroic Strike user must contribute Fight."
            )

        if not self.strike_participants:
            raise ValueError(
                "A combat side must have at least one participant "
                "that can make Strikes."
            )

    @property
    def total_duel_dice(self) -> int:
        """
        Returns the combined Duel dice contributed by all participants.
        """

        return sum(
            participant.duel_dice
            for participant in self.participants
        )

    @property
    def highest_fight(self) -> int:
        """
        Returns the highest Fight value contributed by the side.
        """

        return max(
            participant.profile.fight
            for participant in self.participants
            if participant.contributes_fight
        )

    @property
    def strike_participants(
        self,
    ) -> tuple[CombatParticipant, ...]:
        """
        Returns the participants that may make Strikes
        if this side wins the Duel.
        """

        return tuple(
            participant
            for participant in self.participants
            if participant.can_make_strikes
        )

# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("combat side module loaded successfully.")
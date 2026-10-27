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
    # Army-specific initial resource ceiling. None keeps the legacy profile behaviour.
    effective_starting_might: int | None = None

    @classmethod
    def from_army_entry(cls, entry, *, duel_dice: int,
                        contributes_fight: bool = True,
                        can_make_strikes: bool = True):
        """Bind a combat participant to the fielded entry's effective Might.

        The legacy Profile is preserved for combat statistics; the optional
        ceiling ensures purchased starting Might is honoured separately.
        """
        if not entry.counts_as_model or entry.configured_profile is None:
            raise ValueError("combat participant requires a fielded model entry")
        if entry.quantity != 1:
            raise ValueError("select an individual fielded model from bulk entries")
        return cls(
            profile=entry.profile,
            duel_dice=duel_dice,
            contributes_fight=contributes_fight,
            can_make_strikes=can_make_strikes,
            effective_starting_might=entry.get_attribute("might"),
        )

    def __post_init__(self) -> None:
        value = self.effective_starting_might
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("effective starting Might must be non-negative integer")
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
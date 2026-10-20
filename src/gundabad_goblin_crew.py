"""DEV-077-GUN-C6-B3: Catapult Troll Goblin Crew extra melee Strikes.

This is a *separate* Strength 3 strike source, never Metal Gauntlets.
Combat/target resolution and battlefield wound application stay upstream.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import comb

CATAPULT_TROLL_PROFILE_ID = "GUNDABAD_CATAPULT_TROLL"
CREW_STRIKE_STRENGTH = 3


@dataclass(frozen=True)
class GoblinCrewCombatContext:
    combat_won: bool
    troll_strikes_resolved: bool
    combat_ended_by_brutal_power_attack: bool = False
    crew_able_to_act: bool = True

    def __post_init__(self):
        for name in ("combat_won", "troll_strikes_resolved",
                     "combat_ended_by_brutal_power_attack", "crew_able_to_act"):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be bool")


@dataclass(frozen=True)
class GoblinCrewStrikeResult:
    strikes: int
    strength: int
    wound_probability_per_strike: Fraction
    wound_count_distribution: tuple[Fraction, ...]
    expected_wounds: Fraction


def is_gundabad_catapult_troll(combatant) -> bool:
    configured = getattr(combatant, "active_configured_profile", combatant)
    return getattr(getattr(configured, "profile", None), "id", None) == CATAPULT_TROLL_PROFILE_ID


def can_make_goblin_crew_strikes(combatant, context: GoblinCrewCombatContext) -> bool:
    if not isinstance(context, GoblinCrewCombatContext):
        raise TypeError("Expected GoblinCrewCombatContext")
    return (is_gundabad_catapult_troll(combatant)
            and context.combat_won
            and context.troll_strikes_resolved
            and not context.combat_ended_by_brutal_power_attack
            and context.crew_able_to_act)


def resolve_goblin_crew_strikes(
    combatant, context: GoblinCrewCombatContext, *,
    d6_strikes: int, target_defence: int,
) -> GoblinCrewStrikeResult:
    """Resolve one chosen D6 extra-strike count against a target's Defence.

    Uses the project's canonical wound table; each strike is independently
    rolled To Wound at S3. This is a raw distribution before Fate, saves,
    special target interactions or specific Strike allocation.
    """
    if not can_make_goblin_crew_strikes(combatant, context):
        raise ValueError("Goblin Crew Strikes are not permitted in this Combat")
    if type(d6_strikes) is not int or not 1 <= d6_strikes <= 6:
        raise ValueError("d6_strikes must be a natural D6 result (1-6)")
    if type(target_defence) is not int or not 1 <= target_defence <= 10:
        raise ValueError("target_defence must be an integer from 1 to 10")

    from wound_table import get_wound_target
    from wound_probability import get_wound_probability
    chance = get_wound_probability(get_wound_target(CREW_STRIKE_STRENGTH, target_defence))
    distribution = tuple(
        Fraction(comb(d6_strikes, wounds)) * chance**wounds
        * (1 - chance)**(d6_strikes - wounds)
        for wounds in range(d6_strikes + 1)
    )
    return GoblinCrewStrikeResult(
        strikes=d6_strikes, strength=CREW_STRIKE_STRENGTH,
        wound_probability_per_strike=chance,
        wound_count_distribution=distribution,
        expected_wounds=d6_strikes * chance,
    )


def expected_goblin_crew_strikes(combatant, context: GoblinCrewCombatContext) -> Fraction:
    """Conditional expected extra Strikes; not automatic hit/wound output."""
    return Fraction(7, 2) if can_make_goblin_crew_strikes(combatant, context) else Fraction(0)

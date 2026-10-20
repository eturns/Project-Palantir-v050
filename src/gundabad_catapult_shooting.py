"""DEV-077-GUN-C6-B2: Gundabad Catapult Troll firing exceptions.

Dedicated siege resolver: does not alter generic ranged-weapon eligibility.
Actual line of sight, target designation, arcing scatter, Area Effect, and
application of malfunction wounds remain separate battlefield operations.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import isfinite

CATAPULT_TROLL_PROFILE_ID = 'GUNDABAD_CATAPULT_TROLL'
CATAPULT_MIN_RANGE = 12
CATAPULT_MAX_RANGE = 96
CATAPULT_STRENGTH = 10
HIT_ROLL = 6
MALFUNCTION_ROLL = 1


@dataclass(frozen=True)
class CatapultFiringContext:
    distance_inches: float
    moved_inches: float = 0.0
    engaged_in_combat: bool = False
    troll_alive: bool = True
    crew_operated_by_other_model: bool = False
    line_of_sight_confirmed: bool = True
    other_siege_requirements_met: bool = True

    def __post_init__(self):
        for value, field in ((self.distance_inches, 'distance_inches'),
                             (self.moved_inches, 'moved_inches')):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
                raise ValueError(f'{field} must be a finite nonnegative number.')
        for field in ('engaged_in_combat', 'troll_alive', 'crew_operated_by_other_model',
                      'line_of_sight_confirmed', 'other_siege_requirements_met'):
            if type(getattr(self, field)) is not bool:
                raise TypeError(f'{field} must be bool.')


@dataclass(frozen=True)
class CatapultShotResult:
    natural_roll: int
    hit: bool
    malfunction: bool
    wounds_to_troll: int
    strength: int = CATAPULT_STRENGTH


def is_catapult_troll(shooter) -> bool:
    """Accept a configured profile or a current-form state.

    Not dependent on an assumed wargear ID; canonical profile is required.
    """
    configured = getattr(shooter, 'active_configured_profile', shooter)
    return getattr(getattr(configured, 'profile', None), 'id', None) == CATAPULT_TROLL_PROFILE_ID


def can_fire_catapult(shooter, context: CatapultFiringContext) -> bool:
    if not isinstance(context, CatapultFiringContext):
        raise TypeError('Expected CatapultFiringContext.')
    if not is_catapult_troll(shooter):
        return False
    if not context.troll_alive or context.crew_operated_by_other_model:
        return False
    if not context.line_of_sight_confirmed or not context.other_siege_requirements_met:
        return False
    return CATAPULT_MIN_RANGE <= context.distance_inches <= CATAPULT_MAX_RANGE


def catapult_hit_probability(shooter, context: CatapultFiringContext) -> Fraction:
    return Fraction(1, 6) if can_fire_catapult(shooter, context) else Fraction(0)


def catapult_malfunction_probability(shooter, context: CatapultFiringContext) -> Fraction:
    if not can_fire_catapult(shooter, context) or not context.engaged_in_combat:
        return Fraction(0)
    return Fraction(1, 6)


def resolve_catapult_shot(shooter, context: CatapultFiringContext, natural_roll: int) -> CatapultShotResult:
    if type(natural_roll) is not int or not 1 <= natural_roll <= 6:
        raise ValueError('To Hit result must be a natural D6 roll from 1 to 6.')
    if not can_fire_catapult(shooter, context):
        raise ValueError('The Gundabad Catapult Troll cannot fire in this context.')
    malfunction = context.engaged_in_combat and natural_roll == MALFUNCTION_ROLL
    return CatapultShotResult(
        natural_roll=natural_roll,
        hit=natural_roll == HIT_ROLL,
        malfunction=malfunction,
        wounds_to_troll=1 if malfunction else 0,
    )


def catapult_can_be_destroyed_by_base_contact() -> bool:
    """This combined-profile siege model cannot be destroyed by that action."""
    return False


def catapult_requires_separate_crew() -> bool:
    return False

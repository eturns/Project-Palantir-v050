"""DEV-077-SMAUG-C2/E: bounded, source-linked Breathe Fire evidence.

One shared shooting hit gates all splash victims. Victims are identified by
caller-supplied, measured base distances; no spatial positions are inferred.
The caller must resolve fate/other wound prevention in an actual game state.
No changes to ordinary shooting or dashboard ratings are made here.
"""
from dataclasses import dataclass
from fractions import Fraction

from shooting_hit_probability import get_shooting_hit_probability
from wound_probability import get_wound_probability
from wound_table import get_wound_target

FIRE_RANGE_INCHES = 18
FIRE_RADIUS_INCHES = 2
FIRE_STRENGTH = 10


@dataclass(frozen=True)
class FireVictim:
    model_id: str
    defence: int
    distance_from_hit_base_inches: float
    immune_to_fire: bool = False

    def __post_init__(self):
        if not self.model_id:
            raise ValueError("Victim needs a model ID")
        if not 1 <= self.defence <= 10:
            raise ValueError("Defence must be 1..10")
        if self.distance_from_hit_base_inches < 0:
            raise ValueError("Base separation cannot be negative")
        if type(self.immune_to_fire) is not bool:
            raise TypeError("immune_to_fire must be a bool")


@dataclass(frozen=True)
class FireVictimEvidence:
    model_id: str
    chance_wounded: Fraction
    chance_set_ablaze_if_no_prevention: Fraction
    chance_slain_if_no_prevention: Fraction
    requires_wound_prevention_resolution: bool


@dataclass(frozen=True)
class BreatheFireEvidence:
    hit_probability: Fraction
    impacted: tuple[FireVictimEvidence, ...]
    attack_count: int = 1
    evidence_status: str = "bounded_unprevented_wound_projection"


def calculate_breathe_fire_evidence(*, target_distance_inches: float,
                                    primary_target_id: str,
                                    victims: tuple[FireVictim, ...],
                                    shoot_value: str = "2+",
                                    to_hit_modifier: int = 0) -> BreatheFireEvidence:
    """Compute single-attack hit-gated probabilities for impacted models.

    Primary target's separation is zero. Other models' separation is measured
    from the *hit model*, not from the shooter, to their bases. The probabilities
    deliberately assume no Fate/wound prevention; they MUST NOT be interpreted
    as unconditional kills or as independent shooting attacks. Misses hit nobody
    within this bounded calculation (scatters/missed-shot collisions unsupported).
    """
    if target_distance_inches < 0:
        raise ValueError("Negative range")
    if not primary_target_id:
        raise ValueError("Missing primary target")
    if not victims or len({v.model_id for v in victims}) != len(victims):
        raise ValueError("Victims must be nonempty and have unique IDs")
    primary = [v for v in victims if v.model_id == primary_target_id]
    if len(primary) != 1 or primary[0].distance_from_hit_base_inches != 0:
        raise ValueError("Primary target must appear at distance zero")
    if type(to_hit_modifier) is not int:
        raise TypeError("to_hit_modifier must be an int")
    hit = (get_shooting_hit_probability(shoot_value, modifier=to_hit_modifier)
           if target_distance_inches <= FIRE_RANGE_INCHES else Fraction(0))
    result = []
    for victim in victims:
        if victim.distance_from_hit_base_inches > FIRE_RADIUS_INCHES:
            continue
        if victim.immune_to_fire:
            result.append(FireVictimEvidence(victim.model_id, Fraction(0),
                                             Fraction(0), Fraction(0), False))
            continue
        wound_chance = hit * get_wound_probability(
            get_wound_target(strength=FIRE_STRENGTH, defence=victim.defence)
        )
        # If no prevention applies, wound => slain. Otherwise, an un-slain hit
        # is Set Ablaze. The evidence exposes this conditionality explicitly.
        result.append(FireVictimEvidence(victim.model_id, wound_chance,
                                         hit - wound_chance, wound_chance, True))
    return BreatheFireEvidence(hit, tuple(result))

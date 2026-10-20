"""DEV-077-GUN-C6-A: Gundabad Troll Brute's War Beast impact profile.

This resolver computes *raw* Strength 10 Impact Hit distributions. It does
not simulate movement geometry, apply Fate, or determine casualties from a
single wound: the caller must supply actual post-save survival when advancing
the Trample. Rider and mount are separate impacted components.
"""
from dataclasses import dataclass
from fractions import Fraction

from wound_table import get_wound_target
from wound_probability import get_wound_probability, get_wound_distribution

TROLL_BRUTE_PROFILE_ID = "TROLL_BRUTE"
TRAMPLE_RULE_ID = "TRAMPLE"
IMPACT_STRENGTH = 10
IMPACT_HITS = 2


@dataclass(frozen=True)
class ImpactComponent:
    """One model component contacted during a Trample (rider OR mount)."""
    component_id: str
    defence: int

    def __post_init__(self) -> None:
        if not isinstance(self.component_id, str) or not self.component_id.strip():
            raise ValueError("component_id must be a non-empty string")
        if type(self.defence) is not int or not 1 <= self.defence <= 10:
            raise ValueError("defence must be an integer from 1 to 10")


@dataclass(frozen=True)
class ImpactResult:
    component_id: str
    strength: int
    hit_count: int
    wound_probability_per_hit: Fraction
    raw_wound_distribution: tuple[Fraction, ...]

    @property
    def expected_raw_wounds(self) -> Fraction:
        return self.hit_count * self.wound_probability_per_hit


def _active_profile(combatant):
    return getattr(combatant, "active_configured_profile", combatant)


def has_troll_brute_trample(combatant) -> bool:
    """Check the configured Troll Brute, not its separate Orc Commander."""
    configured = _active_profile(combatant)
    if getattr(getattr(configured, "profile", None), "id", None) != TROLL_BRUTE_PROFILE_ID:
        return False
    return any(
        getattr(getattr(assignment, "rule", None), "id", None) == TRAMPLE_RULE_ID
        for assignment in getattr(configured, "effective_special_rules", ())
    )


def resolve_troll_brute_impact_hits(
    combatant,
    components: tuple[ImpactComponent, ...],
    *,
    is_trampling: bool,
) -> tuple[ImpactResult, ...]:
    """Resolve damage *potential* for an explicitly supplied contact.

    Contact geometry and validity must be verified by the calling War Beast
    movement layer. No damage is emitted for an unqualified combatant or when
    it is not Trampling. A cavalry rider and mount should each be included.
    """
    if type(is_trampling) is not bool:
        raise TypeError("is_trampling must be bool")
    if not isinstance(components, tuple) or any(
        not isinstance(c, ImpactComponent) for c in components
    ):
        raise TypeError("components must be a tuple of ImpactComponent")
    ids = [c.component_id for c in components]
    if len(ids) != len(set(ids)):
        raise ValueError("Each impacted component must appear exactly once")
    if not is_trampling or not has_troll_brute_trample(combatant):
        return ()
    outcomes = []
    for component in components:
        chance = get_wound_probability(
            get_wound_target(IMPACT_STRENGTH, component.defence)
        )
        outcomes.append(ImpactResult(
            component_id=component.component_id,
            strength=IMPACT_STRENGTH,
            hit_count=IMPACT_HITS,
            wound_probability_per_hit=chance,
            raw_wound_distribution=get_wound_distribution(IMPACT_HITS, chance),
        ))
    return tuple(outcomes)


def trample_continues_after_contact(*, target_survived: bool) -> bool:
    """War Beast continues only when the contacted model was slain.

    Call after wound, Fate, prevention and other applicable defences resolve.
    """
    if type(target_survived) is not bool:
        raise TypeError("target_survived must be bool")
    return not target_survived

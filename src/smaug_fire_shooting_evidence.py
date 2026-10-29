"""DEV-077-SMAUG-C2C/E — read-only army-level Breathe Fire evidence.

Projects a single correlated Breathe Fire shot to bounded aggregate offensive
and shooting evidence. This is not a dashboard-calibration adapter and does not
simulate resource consumption, future burn damage, or unobserved positioning.
"""
from dataclasses import dataclass
from fractions import Fraction

from smaug_breathe_fire import FireVictim, calculate_breathe_fire_evidence
from smaug_fire_defensive_resolution import FireDefender, resolve_breathe_fire_defence


@dataclass(frozen=True)
class SmaugFireShootingEvidence:
    source_profile_id: str
    attacks: int
    probability_primary_hit: Fraction
    target_count: int
    expected_wounds_before_prevention: Fraction
    expected_prevented_wounds: Fraction
    expected_immediate_casualties: Fraction
    expected_models_set_ablaze: Fraction
    # No distribution of total casualties is claimed. Victims share one hit roll.
    target_outcomes: tuple
    evidence_status: str = "bounded_area_shooting_expected_values_no_dashboard_scoring"


def calculate_smaug_fire_shooting_evidence(
    *,
    source_profile_id: str,
    target_distance_inches: float,
    primary_target_id: str,
    victims: tuple[FireVictim, ...],
    defenders: tuple[FireDefender, ...],
    shoot_value: str = "2+",
    to_hit_modifier: int = 0,
) -> SmaugFireShootingEvidence:
    """Calculate per-shot expected values, summing linear expectations only.

    Every eligible victim's defence must be provided, including fire-immune
    victims. No claim of statistical independence is made; in particular the
    sum of expected kills is not the chance of eliminating any given group.
    """
    if source_profile_id != "SMAUG":
        raise ValueError("Breathe Fire army evidence requires canonical SMAUG profile")
    attack = calculate_breathe_fire_evidence(
        target_distance_inches=target_distance_inches,
        primary_target_id=primary_target_id,
        victims=victims,
        shoot_value=shoot_value,
        to_hit_modifier=to_hit_modifier,
    )
    resolved = resolve_breathe_fire_defence(attack, defenders)
    return SmaugFireShootingEvidence(
        source_profile_id=source_profile_id,
        attacks=1,
        probability_primary_hit=attack.hit_probability,
        target_count=len(resolved.impacted),
        expected_wounds_before_prevention=sum(
            (x.chance_wounded_before_prevention for x in resolved.impacted), Fraction(0)
        ),
        expected_prevented_wounds=sum(
            (x.chance_wound_prevented for x in resolved.impacted), Fraction(0)
        ),
        expected_immediate_casualties=sum(
            (x.chance_slain for x in resolved.impacted), Fraction(0)
        ),
        expected_models_set_ablaze=sum(
            (x.chance_set_ablaze for x in resolved.impacted), Fraction(0)
        ),
        target_outcomes=resolved.impacted,
    )

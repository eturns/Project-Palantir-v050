"""Pinpoint Shot: explicit special shooting attack resolving one targeted shot.

Normal shooting remains unchanged. A successful To Hit bypasses all In The
Way rolls, but not wound resolution. No line-of-sight exemption is implied.
"""
from fractions import Fraction
from configured_profile import ConfiguredProfile
from ranged_weapon_profile import RangedWeaponProfile
from shooting_attack_count import ShootingMode, get_effective_shooting_attack_count
from shooting_eligibility import ShootingContext, can_shoot
from shooting_wound_probability import get_shooting_wound_probability
from wound_modifier import WoundModifier


def expected_pinpoint_wounds(
    *,
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
    weapon: RangedWeaponProfile,
    context: ShootingContext,
    line_of_sight_clear: bool,
    to_hit_modifier: int = 0,
    wound_modifier: WoundModifier = WoundModifier(),
) -> Fraction:
    """Expected wounds from exactly one Pinpoint shot, not three Deadly shots.

    Rejects missing context rather than silently supplying standard-shooting
    assumptions. The caller must separately establish visible target and legal
    target selection; LOS is not bypassed by the profile rule.
    """
    if context.shooting_mode is not ShootingMode.PINPOINT:
        raise ValueError("Explicit Pinpoint shooting mode required.")
    if not line_of_sight_clear:
        raise ValueError("Target line of sight is blocked.")
    if not can_shoot(shooter=attacker, weapon=weapon, context=context):
        raise ValueError("Pinpoint shooting attack is not eligible.")
    if get_effective_shooting_attack_count(attacker, mode=ShootingMode.PINPOINT) != 1:
        raise ValueError("Pinpoint Shot must consist of exactly one attack.")
    return get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        in_the_way_required_rolls=(),
        cavalry_part_in_the_way_required_roll=None,
        target_is_cavalry=False,
        to_hit_modifier=to_hit_modifier,
        wound_modifier=wound_modifier,
    )

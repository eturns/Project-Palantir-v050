from fractions import Fraction

from configured_profile import ConfiguredProfile
from ranged_weapon_profile import RangedWeaponProfile
from shooting_hit_probability import (
    get_shooting_hit_probability_for_profile,
)
from wound_table import get_wound_target
from in_the_way_probability import (
    get_in_the_way_success_probability,
)
from wound_modifier import WoundModifier
from wound_probability import (
    get_expected_wounds,
    get_modified_wound_probability,
    get_wound_probability,
    get_modified_wound_probability_with_reroll,
)
from wound_reroll import WoundReroll
from shooting_attack_count import (
    get_effective_shooting_attack_count,
)
from shooting_special_rule_wound_reroll import (
    get_shooting_special_rule_wound_reroll,
)
from sharpshooter import (
    requires_cavalry_part_in_the_way_test,
)

def get_shooting_wound_probability(
    *,
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
    weapon: RangedWeaponProfile,
    in_the_way_required_rolls: tuple[int, ...] = (),
    in_the_way_modifier: int = 0,
    to_hit_modifier: int = 0,
    wound_modifier: WoundModifier = WoundModifier(),
    wound_reroll: WoundReroll = WoundReroll(),
    cavalry_part_in_the_way_required_roll: int | None = None,
    target_is_cavalry: bool = False,
) -> Fraction:
    if not weapon.is_mechanically_complete:
        raise ValueError(
            "Ranged weapon mechanics must be complete."
        )

    hit_probability = (
    get_shooting_hit_probability_for_profile(
        attacker,
        modifier=to_hit_modifier,
    )
)

    in_the_way_probability = Fraction(1, 1)

    for required_roll in in_the_way_required_rolls:
        in_the_way_probability *= (
            get_in_the_way_success_probability(
                required_roll=required_roll,
                modifier=in_the_way_modifier,
            )
        )

    if (
        cavalry_part_in_the_way_required_roll is not None
        and requires_cavalry_part_in_the_way_test(
            attacker,
            target_is_cavalry=target_is_cavalry,
        )
    ):
        in_the_way_probability *= (
            get_in_the_way_success_probability(
                required_roll=(
                    cavalry_part_in_the_way_required_roll
                ),
            )
        )

    wound_target = get_wound_target(
        strength=weapon.strength,
        defence=defender.effective_defence,
    )

    special_rule_reroll = (
        get_shooting_special_rule_wound_reroll(
            attacker=attacker,
            weapon=weapon,
        )
    )

    combined_wound_reroll = WoundReroll(
        reroll_failed=(
            wound_reroll.reroll_failed
            or special_rule_reroll.reroll_failed
        ),
        reroll_natural_ones=(
            wound_reroll.reroll_natural_ones
            or special_rule_reroll.reroll_natural_ones
        ),
    )

    wound_probability = (
        get_modified_wound_probability_with_reroll(
            target=wound_target,
            modifier=wound_modifier,
            reroll=combined_wound_reroll,
        )
    )

    return (
        hit_probability
        * in_the_way_probability
        * wound_probability
    )

def get_expected_shooting_wounds(
    *,
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
    weapon: RangedWeaponProfile,
    in_the_way_required_rolls: tuple[int, ...] = (),
    in_the_way_modifier: int = 0,
    to_hit_modifier: int = 0,
    wound_modifier: WoundModifier = WoundModifier(),
) -> Fraction:
    """
    Returns the expected number of wounds caused by all
    shooting attacks made with the ranged weapon.

    The calculation includes the weapon's shot count and
    shooting-attack-count effects such as Expert Shot.
    """

    if not weapon.is_mechanically_complete:
        raise ValueError(
            "Ranged weapon mechanics must be complete."
        )

    wound_probability = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        in_the_way_required_rolls=in_the_way_required_rolls,
        in_the_way_modifier=in_the_way_modifier,
        to_hit_modifier=to_hit_modifier,
        wound_modifier=wound_modifier,
    )

    number_of_shots = (
        weapon.shots
        * get_effective_shooting_attack_count(
            attacker,
        )
    )

    return get_expected_wounds(
        number_of_strikes=number_of_shots,
        wound_probability=wound_probability,
    )
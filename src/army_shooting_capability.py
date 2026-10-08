from fractions import Fraction

from configured_profile import ConfiguredProfile
from ranged_weapon_profile import RangedWeaponProfile
from shooting_wound_probability import (
    get_expected_shooting_wounds,
)
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule
from shooting_eligibility import (
    ShootingContext,
    can_shoot,
)
from shooting_to_hit_modifier import (
    get_movement_shooting_modifier,
)
from army import Army
from ranged_weapon_resolver import (
    resolve_ranged_weapon,
)

def sum_expected_shooting_wounds(
    model_outputs: tuple[Fraction, ...],
) -> Fraction:
    return sum(
        model_outputs,
        start=Fraction(0, 1),
    )


def get_army_expected_shooting_wounds(
    *,
    shooters: tuple[
        tuple[ConfiguredProfile, RangedWeaponProfile]
        | tuple[
            ConfiguredProfile,
            RangedWeaponProfile,
            ShootingContext,
        ],
        ...,
    ],
    defender: ConfiguredProfile,
) -> Fraction:
    model_outputs = []

    for entry in shooters:
        if len(entry) == 2:
            shooter, weapon = entry
            context = ShootingContext()
        else:
            shooter, weapon, context = entry

        if not can_shoot(
            shooter=shooter,
            weapon=weapon,
            context=context,
        ):
            continue

        movement_modifier = (
            get_movement_shooting_modifier(
                shooter,
                moved_this_turn=context.moved_this_turn,
            )
        )

        expected_wounds = get_expected_shooting_wounds(
            attacker=shooter,
            defender=defender,
            weapon=weapon,
            to_hit_modifier=movement_modifier,
        )

        model_outputs.append(expected_wounds)

    return sum_expected_shooting_wounds(
        tuple(model_outputs),
    )

def calculate_shooting_output_density(
    *,
    expected_wounds: Fraction,
    army_points: int,
) -> Fraction:
    if army_points <= 0:
        return Fraction(0, 1)

    return (
        expected_wounds
        * 100
        / army_points
    )

def resolve_army_ranged_shooters(
    army: Army,
) -> tuple[
    tuple[
        ConfiguredProfile,
        RangedWeaponProfile,
    ],
    ...,
]:
    shooters = []

    for fielded_model in army.fielded_models():
        configured_profile = (
            fielded_model.configured_profile
        )

        if configured_profile is None:
            continue

        weapon = resolve_ranged_weapon(
            configured_profile
        )

        if weapon is None:
            continue

        shooters.append(
            (
                configured_profile,
                weapon,
            )
        )

    return tuple(shooters)

def calculate_army_shooting_output_density(
    *,
    army: Army,
    defender: ConfiguredProfile | None,
) -> Fraction:
    shooters = resolve_army_ranged_shooters(
        army
    )

    incomplete_weapons = tuple(
        weapon
        for _, weapon in shooters
        if not weapon.is_mechanically_complete
    )

    if incomplete_weapons:
        raise ValueError(
            "All ranged weapons must be mechanically complete "
            "before calculating army shooting output density."
        )

    if defender is None:
        raise ValueError(
            "A defender profile is required to calculate "
            "army shooting output density."
        )

    expected_wounds = get_army_expected_shooting_wounds(
        shooters=shooters,
        defender=defender,
    )

    return calculate_shooting_output_density(
        expected_wounds=expected_wounds,
        army_points=army.total_points(),
    )
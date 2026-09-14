from configured_profile import ConfiguredProfile
from effective_defence import get_effective_defence
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from melee_weapon_selection import MeleeWeaponSelection
from reroll_effect_resolver import (
    resolved_wound_reroll,
)
from roll_modifier_effect_resolver import (
    resolved_wound_modifier,
)
from special_rule_mechanical_effect_definitions import (
    get_special_rule_mechanical_effect_definitions,
)
from special_rule_wound_effect import (
    get_contextual_special_rule_wound_reroll,
)
from special_rule_wound_modifier import (
    get_special_rule_wound_modifiers,
)
from wargear_mechanical_effect_definitions import (
    get_wargear_mechanical_effect_definitions,
)
from wound_context import WoundContext
from wound_modifier import combine_wound_modifiers
from wound_probability import (
    get_modified_wound_probability_with_reroll,
)
from wound_reroll import WoundReroll
from wound_table import get_wound_target


def calculate_configured_wound_probability(
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
    attacker_selection: MeleeWeaponSelection | None = None,
    context: WoundContext | None = None,
):
    target = get_wound_target(
        strength=attacker.profile.strength,
        defence=get_effective_defence(
            attacker,
            defender,
        ),
    )

    wargear_definitions = (
        get_wargear_mechanical_effect_definitions(
            attacker,
            selection=attacker_selection,
        )
    )

    special_rule_definitions = (
        get_special_rule_mechanical_effect_definitions(
            attacker,
        )
    )

    generic_modifier_definitions = tuple(
        definition
        for definition in wargear_definitions
        if (
            definition.effect.target
            is MechanicalEffectTarget.TO_WOUND_ROLL
            and definition.effect.effect_type
            is MechanicalEffectType.ROLL_MODIFIER
        )
    )

    generic_reroll_definitions = tuple(
        definition
        for definition in special_rule_definitions
        if (
            definition.effect.target
            is MechanicalEffectTarget.TO_WOUND_ROLL
            and definition.effect.effect_type
            is MechanicalEffectType.REROLL
        )
    )

    generic_modifier = resolved_wound_modifier(
        generic_modifier_definitions,
    )

    modifier = combine_wound_modifiers(
        (generic_modifier,)
        + get_special_rule_wound_modifiers(
            attacker,
            defender,
            context=context,
        )
    )

    generic_reroll = resolved_wound_reroll(
        generic_reroll_definitions,
    )

    contextual_reroll = (
        get_contextual_special_rule_wound_reroll(
            attacker,
            selection=attacker_selection,
            defender=defender,
            context=context,
        )
    )

    reroll = WoundReroll(
        reroll_failed=(
            (
                generic_reroll is not None
                and generic_reroll.reroll_failed
            )
            or contextual_reroll.reroll_failed
        ),
        reroll_natural_ones=(
            (
                generic_reroll is not None
                and generic_reroll.reroll_natural_ones
            )
            or contextual_reroll.reroll_natural_ones
        ),
    )

    return get_modified_wound_probability_with_reroll(
        target=target,
        modifier=modifier,
        reroll=reroll,
    )
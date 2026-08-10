from configured_profile import ConfiguredProfile
from wound_modifier import combine_wound_modifiers
from wound_probability import (
    get_modified_wound_probability_with_reroll,
)
from wound_table import get_wound_target
from wargear_wound_effect import (
    get_wargear_wound_modifiers,
)
from melee_weapon_selection import MeleeWeaponSelection
from special_rule_wound_effect import (
    get_special_rule_wound_reroll,
)
from special_rule_wound_modifier import (
    get_special_rule_wound_modifiers,
)
from wound_context import WoundContext
from effective_defence import get_effective_defence

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

    modifier = combine_wound_modifiers(
        get_wargear_wound_modifiers(
            attacker,
            selection=attacker_selection,
        )
        + get_special_rule_wound_modifiers(
            attacker,
            defender,
            context=context,
        )
    )

    reroll = get_special_rule_wound_reroll(
        attacker,
        selection=attacker_selection,
        defender=defender,
        context=context,
    )

    return get_modified_wound_probability_with_reroll(
        target=target,
        modifier=modifier,
        reroll=reroll,
    )
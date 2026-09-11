from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from roll_modifier_effect_resolver import (
    combined_roll_modifier_value,
)
from wargear_mechanical_effect_definitions import (
    get_wargear_mechanical_effect_definitions,
)
from wargear_wound_effect import (
    get_wargear_wound_modifiers,
)

from test_wargear_mechanical_effect_definitions import (
    make_profile_with_two_handed_weapon,
)


def test_generic_two_handed_wound_modifier_matches_legacy_value():
    configured_profile = (
        make_profile_with_two_handed_weapon()
    )

    legacy_modifiers = get_wargear_wound_modifiers(
        configured_profile,
    )

    generic_definitions = tuple(
        definition
        for definition
        in get_wargear_mechanical_effect_definitions(
            configured_profile,
        )
        if (
            definition.effect.target
            is MechanicalEffectTarget.TO_WOUND_ROLL
        )
    )

    legacy_value = sum(
        modifier.to_wound
        for modifier in legacy_modifiers
    )

    generic_value = combined_roll_modifier_value(
        generic_definitions,
    )

    assert generic_value == legacy_value
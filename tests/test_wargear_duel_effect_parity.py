from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from roll_modifier_effect_resolver import (
    combined_roll_modifier_value,
)
from wargear_duel_effect import (
    get_wargear_duel_modifiers,
)
from wargear_mechanical_effect_definitions import (
    get_wargear_mechanical_effect_definitions,
)

from test_wargear_mechanical_effect_definitions import (
    make_profile_with_two_handed_weapon,
)


def get_generic_duel_definitions(
    configured_profile,
    *,
    additional_burly: bool = False,
):
    return tuple(
        definition
        for definition
        in get_wargear_mechanical_effect_definitions(
            configured_profile,
            additional_burly=additional_burly,
        )
        if (
            definition.effect.target
            is MechanicalEffectTarget.DUEL_ROLL
        )
    )


def test_generic_two_handed_duel_modifier_matches_legacy():
    configured_profile = (
        make_profile_with_two_handed_weapon()
    )

    legacy_modifiers = get_wargear_duel_modifiers(
        configured_profile,
    )

    generic_definitions = get_generic_duel_definitions(
        configured_profile,
    )

    legacy_value = sum(
        modifier.value
        for modifier in legacy_modifiers
    )

    generic_value = combined_roll_modifier_value(
        generic_definitions,
    )

    assert generic_value == legacy_value == -1


def test_generic_burly_suppression_matches_legacy():
    configured_profile = (
        make_profile_with_two_handed_weapon(
            has_burly=True,
        )
    )

    legacy_modifiers = get_wargear_duel_modifiers(
        configured_profile,
    )

    generic_definitions = get_generic_duel_definitions(
        configured_profile,
    )

    assert legacy_modifiers == ()
    assert generic_definitions == ()


def test_generic_additional_burly_matches_legacy():
    configured_profile = (
        make_profile_with_two_handed_weapon()
    )

    legacy_modifiers = get_wargear_duel_modifiers(
        configured_profile,
        additional_burly=True,
    )

    generic_definitions = get_generic_duel_definitions(
        configured_profile,
        additional_burly=True,
    )

    assert legacy_modifiers == ()
    assert generic_definitions == ()
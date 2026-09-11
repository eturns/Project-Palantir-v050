from reroll_effect_resolver import (
    resolved_reroll_scopes,
)
from special_rule_mechanical_effect_definitions import (
    BANE_OF_KINGS_RULE_ID,
    POISONED_ATTACKS_RULE_ID,
    get_special_rule_mechanical_effect_definitions,
)
from special_rule_wound_effect import (
    get_special_rule_wound_reroll,
)

from test_special_rule_mechanical_effect_definitions import (
    make_configured_profile,
)


def test_bane_of_kings_generic_reroll_matches_legacy():
    configured_profile = make_configured_profile(
        (BANE_OF_KINGS_RULE_ID,),
    )

    legacy = get_special_rule_wound_reroll(
        configured_profile,
    )

    generic = resolved_reroll_scopes(
        get_special_rule_mechanical_effect_definitions(
            configured_profile,
        )
    )

    assert legacy.reroll_failed is True
    assert legacy.reroll_natural_ones is False

    assert {
        scope.value
        for scope in generic
    } == {
        "FAILED",
    }


def test_poisoned_attacks_generic_reroll_matches_legacy():
    configured_profile = make_configured_profile(
        (POISONED_ATTACKS_RULE_ID,),
    )

    legacy = get_special_rule_wound_reroll(
        configured_profile,
    )

    generic = resolved_reroll_scopes(
        get_special_rule_mechanical_effect_definitions(
            configured_profile,
        )
    )

    assert legacy.reroll_failed is False
    assert legacy.reroll_natural_ones is True

    assert {
        scope.value
        for scope in generic
    } == {
        "NATURAL_ONES",
    }


def test_combined_generic_rerolls_match_legacy():
    configured_profile = make_configured_profile(
        (
            BANE_OF_KINGS_RULE_ID,
            POISONED_ATTACKS_RULE_ID,
        ),
    )

    legacy = get_special_rule_wound_reroll(
        configured_profile,
    )

    generic = resolved_reroll_scopes(
        get_special_rule_mechanical_effect_definitions(
            configured_profile,
        )
    )

    assert legacy.reroll_failed is True
    assert legacy.reroll_natural_ones is True

    assert {
        scope.value
        for scope in generic
    } == {
        "FAILED",
        "NATURAL_ONES",
    }
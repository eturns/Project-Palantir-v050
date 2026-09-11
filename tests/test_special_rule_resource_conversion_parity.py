from resource_conversion_effect_resolver import (
    resolved_resource_conversions,
)
from special_rule_mechanical_effect_definitions import (
    HE_CANNOT_YET_TAKE_PHYSICAL_FORM_RULE_ID,
    get_special_rule_mechanical_effect_definitions,
)
from special_rule_resource_conversions import (
    get_special_rule_resource_conversions,
)

from test_special_rule_mechanical_effect_definitions import (
    make_configured_profile,
)


def test_physical_form_generic_conversion_matches_legacy():
    configured_profile = make_configured_profile(
        (
            HE_CANNOT_YET_TAKE_PHYSICAL_FORM_RULE_ID,
        ),
    )

    legacy = set(
        get_special_rule_resource_conversions(
            (
                HE_CANNOT_YET_TAKE_PHYSICAL_FORM_RULE_ID,
            )
        )
    )

    generic = resolved_resource_conversions(
        get_special_rule_mechanical_effect_definitions(
            configured_profile,
        )
    )

    assert generic == legacy


def test_unrelated_rule_generic_conversion_matches_legacy():
    configured_profile = make_configured_profile(
        ("UNRELATED_RULE",),
    )

    legacy = set(
        get_special_rule_resource_conversions(
            ("UNRELATED_RULE",)
        )
    )

    generic = resolved_resource_conversions(
        get_special_rule_mechanical_effect_definitions(
            configured_profile,
        )
    )

    assert generic == legacy == set()
from resource_conversion_effect_resolver import (
    resolved_resource_conversions,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from special_rule_mechanical_effect_definitions import (
    HE_CANNOT_YET_TAKE_PHYSICAL_FORM_RULE_ID,
    get_special_rule_mechanical_effect_definitions,
)

from test_special_rule_mechanical_effect_definitions import (
    make_configured_profile,
)


def test_physical_form_rule_creates_will_to_fate_conversion():
    configured_profile = make_configured_profile(
        (
            HE_CANNOT_YET_TAKE_PHYSICAL_FORM_RULE_ID,
        ),
    )

    definitions = (
        get_special_rule_mechanical_effect_definitions(
            configured_profile,
        )
    )

    conversions = resolved_resource_conversions(
        definitions,
    )

    assert len(conversions) == 1

    conversion = next(iter(conversions))

    assert (
        conversion.source_resource_type
        is ResourceType.WILL
    )
    assert (
        conversion.target_resource_use
        is ResourceUse.TAKE_FATE
    )


def test_unrelated_rule_creates_no_resource_conversion():
    configured_profile = make_configured_profile(
        ("UNRELATED_RULE",),
    )

    definitions = (
        get_special_rule_mechanical_effect_definitions(
            configured_profile,
        )
    )

    conversions = resolved_resource_conversions(
        definitions,
    )

    assert conversions == set()
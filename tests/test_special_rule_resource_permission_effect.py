from resource_permission_effect_resolver import (
    resolved_resource_permissions,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from special_rule_mechanical_effect_definitions import (
    UNHOLY_RESURRECTION_RULE_ID,
    get_special_rule_mechanical_effect_definitions,
)

from test_special_rule_mechanical_effect_definitions import (
    make_configured_profile,
)


def test_unholy_resurrection_creates_will_permission():
    configured_profile = make_configured_profile(
        (UNHOLY_RESURRECTION_RULE_ID,),
    )

    definitions = (
        get_special_rule_mechanical_effect_definitions(
            configured_profile,
        )
    )

    permissions = resolved_resource_permissions(
        definitions,
    )

    assert permissions == {
        (
            ResourceType.WILL,
            ResourceUse.BOOST_RESURRECTION,
        ),
    }


def test_unrelated_rule_creates_no_resource_permission():
    configured_profile = make_configured_profile(
        ("UNRELATED_RULE",),
    )

    definitions = (
        get_special_rule_mechanical_effect_definitions(
            configured_profile,
        )
    )

    permissions = resolved_resource_permissions(
        definitions,
    )

    assert permissions == set()
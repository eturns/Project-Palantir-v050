from resource_owner import ResourceOwner
from resource_permission_effect_resolver import (
    resolved_resource_permissions,
)
from special_rule_mechanical_effect_definitions import (
    UNHOLY_RESURRECTION_RULE_ID,
    get_special_rule_mechanical_effect_definitions,
)
from special_rule_resource_permissions import (
    get_special_rule_resource_permissions,
)

from resource_owner import ResourceOwner
from resource_permission_effect_resolver import (
    resolved_resource_permissions,
)
from special_rule_mechanical_effect_definitions import (
    UNHOLY_RESURRECTION_RULE_ID,
    get_special_rule_mechanical_effect_definitions,
)
from special_rule_resource_permissions import (
    get_special_rule_resource_permissions,
)

from test_special_rule_mechanical_effect_definitions import (
    make_configured_profile,
)


def test_unholy_resurrection_generic_permission_matches_legacy():
    configured_profile = make_configured_profile(
        (UNHOLY_RESURRECTION_RULE_ID,),
    )

    owner = ResourceOwner(
        fielded_model_id="TEST-1",
    )

    legacy_permissions = (
        get_special_rule_resource_permissions(
            owner,
            (UNHOLY_RESURRECTION_RULE_ID,),
        )
    )

    legacy_pairs = {
        (
            permission.resource_type,
            permission.resource_use,
        )
        for permission in legacy_permissions
    }

    generic_pairs = resolved_resource_permissions(
        get_special_rule_mechanical_effect_definitions(
            configured_profile,
        )
    )

    assert generic_pairs == legacy_pairs


def test_unrelated_rule_generic_permission_matches_legacy():
    configured_profile = make_configured_profile(
        ("UNRELATED_RULE",),
    )

    owner = ResourceOwner(
        fielded_model_id="TEST-1",
    )

    legacy_permissions = (
        get_special_rule_resource_permissions(
            owner,
            ("UNRELATED_RULE",),
        )
    )

    legacy_pairs = {
        (
            permission.resource_type,
            permission.resource_use,
        )
        for permission in legacy_permissions
    }

    generic_pairs = resolved_resource_permissions(
        get_special_rule_mechanical_effect_definitions(
            configured_profile,
        )
    )

    assert generic_pairs == legacy_pairs == set()
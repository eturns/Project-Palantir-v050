from resource_conversion import ResourceConversion
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from special_rule_resource_conversions import (
    get_special_rule_resource_conversions,
)
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from resource_owner import ResourceOwner
from special_rule_resource_permissions import (
    get_special_rule_resource_permissions,
)

def test_he_cannot_yet_take_physical_form_grants_will_as_fate_conversion():
    result = get_special_rule_resource_conversions(
        special_rule_ids=(
            "HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
        ),
    )

    assert result == (
        ResourceConversion(
            source_resource_type=ResourceType.WILL,
            target_resource_use=ResourceUse.TAKE_FATE,
        ),
    )


def test_unrelated_special_rule_grants_no_resource_conversion():
    result = get_special_rule_resource_conversions(
        special_rule_ids=(
            "TERROR",
        ),
    )

    assert result == ()

def test_unholy_resurrection_grants_will_boost_resurrection_permission():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    result = get_special_rule_resource_permissions(
        owner=owner,
        special_rule_ids=(
            "UNHOLY_RESURRECTION",
        ),
    )

    assert result == (
        OwnedResourceUsePermission(
            owner=owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.BOOST_RESURRECTION,
        ),
    )


def test_unrelated_rule_grants_no_special_resource_permission():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    result = get_special_rule_resource_permissions(
        owner=owner,
        special_rule_ids=(
            "TERROR",
        ),
    )

    assert result == ()
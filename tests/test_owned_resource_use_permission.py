from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)


def test_owned_permission_stores_owner_resource_and_use():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    permission = OwnedResourceUsePermission(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.CAST_SPELL,
    )

    assert permission.owner == owner
    assert permission.resource_type == ResourceType.WILL
    assert permission.resource_use == ResourceUse.CAST_SPELL


def test_permissions_for_repeated_models_are_distinct():
    first_owner = ResourceOwner(
        profile_id="DG_SM",
        instance_index=1,
    )

    second_owner = ResourceOwner(
        profile_id="DG_SM",
        instance_index=2,
    )

    first_permission = OwnedResourceUsePermission(
        owner=first_owner,
        resource_type=ResourceType.MIGHT,
        resource_use=ResourceUse.MODIFY_DUEL,
    )

    second_permission = OwnedResourceUsePermission(
        owner=second_owner,
        resource_type=ResourceType.MIGHT,
        resource_use=ResourceUse.MODIFY_DUEL,
    )

    assert first_permission != second_permission


def test_equivalent_owned_permissions_are_equal():
    permission_a = OwnedResourceUsePermission(
        owner=ResourceOwner(
            profile_id="DG_WK",
            instance_index=1,
        ),
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.RESIST_MAGIC,
    )

    permission_b = OwnedResourceUsePermission(
        owner=ResourceOwner(
            profile_id="DG_WK",
            instance_index=1,
        ),
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.RESIST_MAGIC,
    )

    assert permission_a == permission_b
from owned_resource_use_legality import (
    is_owned_resource_use_permitted,
)
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from army import Army
from owned_resource_use_permission_initialization import (
    get_initial_owned_resource_use_permissions,
)
from profiles import Profile

def test_default_resource_use_is_permitted_for_owner():
    owner = ResourceOwner(
        profile_id="DG_WK",
        instance_index=1,
    )

    assert is_owned_resource_use_permitted(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.CAST_SPELL,
        permissions=(),
    )


def test_default_illegal_resource_use_remains_illegal_without_permission():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    assert not is_owned_resource_use_permitted(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
        permissions=(),
    )


def test_explicit_owner_permission_allows_non_default_resource_use():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    permission = OwnedResourceUsePermission(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
    )

    assert is_owned_resource_use_permitted(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
        permissions=(permission,),
    )


def test_permission_for_one_owner_does_not_apply_to_another_owner():
    permitted_owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    other_owner = ResourceOwner(
        profile_id="DG_WK",
        instance_index=1,
    )

    permission = OwnedResourceUsePermission(
        owner=permitted_owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
    )

    assert not is_owned_resource_use_permitted(
        owner=other_owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
        permissions=(permission,),
    )


def test_permission_must_match_resource_type():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    permission = OwnedResourceUsePermission(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
    )

    assert not is_owned_resource_use_permitted(
        owner=owner,
        resource_type=ResourceType.MIGHT,
        resource_use=ResourceUse.TAKE_FATE,
        permissions=(permission,),
    )


def test_permission_must_match_resource_use():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    permission = OwnedResourceUsePermission(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
    )

    assert not is_owned_resource_use_permitted(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.MODIFY_DUEL,
        permissions=(permission,),
    )

def make_profile_with_special_resource_permission(
    profile_id: str,
    resource_type: ResourceType,
    resource_use: ResourceUse,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=80,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="4+",
        might=1,
        will=1,
        fate=1,
        max_in_army=0,
        special_resource_permissions=(
            (
                resource_type,
                resource_use,
            ),
        ),
    )


def test_profile_declared_permission_is_legal_for_matching_physical_owner():
    army = Army()

    army.add_profile(
        make_profile_with_special_resource_permission(
            profile_id="DG_NEC",
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.TAKE_FATE,
        ),
        quantity=1,
    )

    permissions = get_initial_owned_resource_use_permissions(
        army,
    )

    assert is_owned_resource_use_permitted(
        owner=ResourceOwner(
            profile_id="DG_NEC",
            instance_index=1,
        ),
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
        permissions=permissions,
    )
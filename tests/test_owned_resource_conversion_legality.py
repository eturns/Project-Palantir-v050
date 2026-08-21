from owned_resource_conversion import (
    OwnedResourceConversion,
)
from owned_resource_conversion_legality import (
    is_owned_resource_conversion_permitted,
)
from resource_conversion import ResourceConversion
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def test_matching_owner_can_use_owned_conversion():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    conversion = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    owned_conversion = OwnedResourceConversion(
        owner=owner,
        conversion=conversion,
    )

    assert is_owned_resource_conversion_permitted(
        owner=owner,
        conversion=conversion,
        conversions=(owned_conversion,),
    )


def test_conversion_for_one_owner_does_not_apply_to_another_owner():
    permitted_owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    other_owner = ResourceOwner(
        profile_id="DG_WK",
        instance_index=1,
    )

    conversion = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    owned_conversion = OwnedResourceConversion(
        owner=permitted_owner,
        conversion=conversion,
    )

    assert not is_owned_resource_conversion_permitted(
        owner=other_owner,
        conversion=conversion,
        conversions=(owned_conversion,),
    )


def test_conversion_must_match_source_resource_type():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    permitted_conversion = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    requested_conversion = ResourceConversion(
        source_resource_type=ResourceType.MIGHT,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    owned_conversion = OwnedResourceConversion(
        owner=owner,
        conversion=permitted_conversion,
    )

    assert not is_owned_resource_conversion_permitted(
        owner=owner,
        conversion=requested_conversion,
        conversions=(owned_conversion,),
    )


def test_conversion_must_match_target_resource_use():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    permitted_conversion = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    requested_conversion = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.MODIFY_DUEL,
    )

    owned_conversion = OwnedResourceConversion(
        owner=owner,
        conversion=permitted_conversion,
    )

    assert not is_owned_resource_conversion_permitted(
        owner=owner,
        conversion=requested_conversion,
        conversions=(owned_conversion,),
    )
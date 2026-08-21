from owned_resource_conversion import (
    OwnedResourceConversion,
)
from resource_conversion import ResourceConversion
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def test_owned_conversion_stores_owner_and_conversion():
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

    assert owned_conversion.owner == owner
    assert owned_conversion.conversion == conversion


def test_repeated_model_instances_have_distinct_owned_conversions():
    conversion = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    first = OwnedResourceConversion(
        owner=ResourceOwner(
            profile_id="DG_SM",
            instance_index=1,
        ),
        conversion=conversion,
    )

    second = OwnedResourceConversion(
        owner=ResourceOwner(
            profile_id="DG_SM",
            instance_index=2,
        ),
        conversion=conversion,
    )

    assert first != second


def test_equivalent_owned_conversions_are_equal():
    conversion_a = OwnedResourceConversion(
        owner=ResourceOwner(
            profile_id="DG_NEC",
            instance_index=1,
        ),
        conversion=ResourceConversion(
            source_resource_type=ResourceType.WILL,
            target_resource_use=ResourceUse.TAKE_FATE,
        ),
    )

    conversion_b = OwnedResourceConversion(
        owner=ResourceOwner(
            profile_id="DG_NEC",
            instance_index=1,
        ),
        conversion=ResourceConversion(
            source_resource_type=ResourceType.WILL,
            target_resource_use=ResourceUse.TAKE_FATE,
        ),
    )

    assert conversion_a == conversion_b
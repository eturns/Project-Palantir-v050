from resource_conversion import ResourceConversion
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def test_resource_conversion_stores_source_resource_and_target_use():
    conversion = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    assert (
        conversion.source_resource_type
        == ResourceType.WILL
    )

    assert (
        conversion.target_resource_use
        == ResourceUse.TAKE_FATE
    )


def test_equivalent_resource_conversions_are_equal():
    conversion_a = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    conversion_b = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    assert conversion_a == conversion_b


def test_different_resource_conversions_are_distinct():
    will_as_fate = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    might_for_fate = ResourceConversion(
        source_resource_type=ResourceType.MIGHT,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    assert will_as_fate != might_for_fate
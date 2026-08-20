from resource_use import ResourceUse
from resource_use_permission import (
    ResourceType,
    is_resource_use_permitted,
)


def test_might_can_modify_duel():
    assert is_resource_use_permitted(
        resource_type=ResourceType.MIGHT,
        resource_use=ResourceUse.MODIFY_DUEL,
    )


def test_might_can_modify_wound():
    assert is_resource_use_permitted(
        resource_type=ResourceType.MIGHT,
        resource_use=ResourceUse.MODIFY_WOUND,
    )


def test_will_can_cast_spell():
    assert is_resource_use_permitted(
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.CAST_SPELL,
    )


def test_will_can_resist_magic():
    assert is_resource_use_permitted(
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.RESIST_MAGIC,
    )


def test_fate_can_take_fate():
    assert is_resource_use_permitted(
        resource_type=ResourceType.FATE,
        resource_use=ResourceUse.TAKE_FATE,
    )


def test_will_cannot_take_fate_by_default():
    assert not is_resource_use_permitted(
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
    )


def test_fate_cannot_cast_spell():
    assert not is_resource_use_permitted(
        resource_type=ResourceType.FATE,
        resource_use=ResourceUse.CAST_SPELL,
    )


def test_might_cannot_resist_magic():
    assert not is_resource_use_permitted(
        resource_type=ResourceType.MIGHT,
        resource_use=ResourceUse.RESIST_MAGIC,
    )
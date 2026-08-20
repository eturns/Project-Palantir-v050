import pytest

from resource_owner import ResourceOwner


def test_resource_owner_stores_profile_id_and_instance_index():
    owner = ResourceOwner(
        profile_id="DG_SM",
        instance_index=1,
    )

    assert owner.profile_id == "DG_SM"
    assert owner.instance_index == 1


def test_resource_owner_distinguishes_repeated_profile_instances():
    first_owner = ResourceOwner(
        profile_id="DG_SM",
        instance_index=1,
    )

    second_owner = ResourceOwner(
        profile_id="DG_SM",
        instance_index=2,
    )

    assert first_owner != second_owner


def test_equivalent_resource_owners_are_equal():
    first_owner = ResourceOwner(
        profile_id="DG_SM",
        instance_index=1,
    )

    second_owner = ResourceOwner(
        profile_id="DG_SM",
        instance_index=1,
    )

    assert first_owner == second_owner


def test_resource_owner_key_is_deterministic():
    owner = ResourceOwner(
        profile_id="DG_SM",
        instance_index=2,
    )

    assert owner.key == "DG_SM:2"


@pytest.mark.parametrize(
    "instance_index",
    (
        0,
        -1,
    ),
)
def test_resource_owner_rejects_non_positive_instance_index(
    instance_index,
):
    with pytest.raises(
        ValueError,
        match="instance index must be at least 1",
    ):
        ResourceOwner(
            profile_id="DG_SM",
            instance_index=instance_index,
        )
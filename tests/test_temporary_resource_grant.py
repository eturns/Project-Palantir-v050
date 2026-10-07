import pytest

from resource_owner import ResourceOwner
from resource_use_permission import ResourceType
from temporary_resource_grant import (
    TemporaryResourceGrant,
)


def test_temporary_resource_grant_stores_owner_resource_and_amount():
    owner = ResourceOwner(
        fielded_model_id="TEST:1:1",
    )

    grant = TemporaryResourceGrant(
        owner=owner,
        resource_type=ResourceType.MIGHT,
        amount=1,
    )

    assert grant.owner == owner
    assert grant.resource_type is ResourceType.MIGHT
    assert grant.amount == 1


def test_temporary_resource_grant_defaults_to_one():
    owner = ResourceOwner(
        fielded_model_id="TEST:1:1",
    )

    grant = TemporaryResourceGrant(
        owner=owner,
        resource_type=ResourceType.MIGHT,
    )

    assert grant.amount == 1


def test_temporary_resource_grant_rejects_negative_amount():
    owner = ResourceOwner(
        fielded_model_id="TEST:1:1",
    )

    with pytest.raises(
        ValueError,
        match="Temporary resource amount cannot be negative.",
    ):
        TemporaryResourceGrant(
            owner=owner,
            resource_type=ResourceType.MIGHT,
            amount=-1,
        )
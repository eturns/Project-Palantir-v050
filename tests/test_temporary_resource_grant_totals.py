from resource_owner import ResourceOwner
from resource_use_permission import ResourceType
from temporary_resource_grant import (
    TemporaryResourceGrant,
)
from temporary_resource_grant_totals import (
    calculate_temporary_resource_total,
)


def test_temporary_resource_total_is_owner_and_resource_specific():
    first_owner = ResourceOwner(
        fielded_model_id="FIRST:1:1",
    )

    second_owner = ResourceOwner(
        fielded_model_id="SECOND:1:1",
    )

    grants = (
        TemporaryResourceGrant(
            owner=first_owner,
            resource_type=ResourceType.MIGHT,
            amount=1,
        ),
        TemporaryResourceGrant(
            owner=first_owner,
            resource_type=ResourceType.WILL,
            amount=2,
        ),
        TemporaryResourceGrant(
            owner=second_owner,
            resource_type=ResourceType.MIGHT,
            amount=3,
        ),
    )

    assert (
        calculate_temporary_resource_total(
            grants=grants,
            owner=first_owner,
            resource_type=ResourceType.MIGHT,
        )
        == 1
    )
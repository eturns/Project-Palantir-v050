from resource_owner import ResourceOwner
from resource_use_permission import ResourceType
from temporary_resource_grant import (
    TemporaryResourceGrant,
)


MIGHTY_HERO_RULE_ID = "MIGHTY_HERO"


def get_special_rule_temporary_resource_grants(
    owner: ResourceOwner,
    rule_ids: frozenset[str],
) -> tuple[TemporaryResourceGrant, ...]:
    grants: list[
        TemporaryResourceGrant
    ] = []

    if MIGHTY_HERO_RULE_ID in rule_ids:
        grants.append(
            TemporaryResourceGrant(
                owner=owner,
                resource_type=ResourceType.MIGHT,
                amount=1,
            )
        )

    return tuple(grants)
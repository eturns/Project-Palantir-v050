from army_definition import ArmyDefinition
from profile_quantity_relation_rule import (
    ProfileQuantityRelationRule,
)


def profile_quantity_relation_rule_allows(
    rule: ProfileQuantityRelationRule,
    definition: ArmyDefinition,
) -> bool:
    limited_quantity = sum(
        entry.quantity
        for entry in definition.entries
        if entry.profile_id == rule.limited_profile_id
    )

    reference_quantity = sum(
        entry.quantity
        for entry in definition.entries
        if entry.profile_id == rule.reference_profile_id
    )

    return limited_quantity <= reference_quantity
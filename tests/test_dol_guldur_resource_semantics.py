from hero_resource_state import HeroResourceState
from master_of_the_nazgul_aura import (
    get_master_of_the_nazgul_aura_range_inches,
)
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from resource_conversion import ResourceConversion
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from special_rule_resource_conversions import (
    get_special_rule_resource_conversions,
)
from special_rule_resource_permissions import (
    get_special_rule_resource_permissions,
)
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules

def test_necromancer_special_rules_expose_expected_resource_semantics():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    special_rule_ids = (
        "HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
        "UNHOLY_RESURRECTION",
        "MASTER_OF_THE_NAZGUL",
    )

    conversions = tuple(
        OwnedResourceConversion(
            owner=owner,
            conversion=conversion,
        )
        for conversion in get_special_rule_resource_conversions(
            special_rule_ids=special_rule_ids,
        )
    )

    permissions = get_special_rule_resource_permissions(
        owner=owner,
        special_rule_ids=special_rule_ids,
    )

    assert conversions == (
        OwnedResourceConversion(
            owner=owner,
            conversion=ResourceConversion(
                source_resource_type=ResourceType.WILL,
                target_resource_use=ResourceUse.TAKE_FATE,
            ),
        ),
    )

    assert permissions == (
        OwnedResourceUsePermission(
            owner=owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.BOOST_RESURRECTION,
        ),
    )


def test_necromancer_remaining_will_changes_master_aura_range():
    assert (
        get_master_of_the_nazgul_aura_range_inches(
            HeroResourceState(
                remaining_might=3,
                remaining_will=20,
                remaining_fate=0,
            )
        )
        == 18
    )

    assert (
        get_master_of_the_nazgul_aura_range_inches(
            HeroResourceState(
                remaining_might=3,
                remaining_will=19,
                remaining_fate=0,
            )
        )
        == 12
    )

    assert (
        get_master_of_the_nazgul_aura_range_inches(
            HeroResourceState(
                remaining_might=3,
                remaining_will=9,
                remaining_fate=0,
            )
        )
        == 6
    )

def test_necromancer_loaded_profile_has_will_as_fate_rule():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    special_rules = load_special_rules()

    load_profile_special_rules(
        profiles_by_id,
        special_rules,
    )

    necromancer = profiles_by_id["DG_NEC"]

    special_rule_ids = {
        assignment.rule.id
        for assignment in necromancer.special_rules
    }

    assert (
        "HE_CANNOT_YET_TAKE_PHYSICAL_FORM"
        in special_rule_ids
    )
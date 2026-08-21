from army import Army
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from owned_resource_use_permission_initialization import (
    get_initial_owned_resource_use_permissions,
)
from profiles import Profile
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule

def make_profile(
    profile_id: str,
    special_resource_permissions: tuple[
        tuple[ResourceType, ResourceUse],
        ...,
    ] = (),
    special_rules=None,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=80,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="4+",
        might=1,
        will=1,
        fate=1,
        max_in_army=0,
        special_resource_permissions=special_resource_permissions,
        special_rules=(
            []
            if special_rules is None
            else special_rules
        ),
    )


def test_default_army_initializes_with_no_special_permissions():
    army = Army()

    army.add_profile(
        make_profile("DG_WK"),
        quantity=1,
    )

    result = get_initial_owned_resource_use_permissions(
        army,
    )

    assert result == ()


def test_profile_declared_permission_is_created_for_owner():
    army = Army()

    army.add_profile(
        make_profile(
            "DG_NEC",
            special_resource_permissions=(
                (
                    ResourceType.WILL,
                    ResourceUse.TAKE_FATE,
                ),
            ),
        ),
        quantity=1,
    )

    result = get_initial_owned_resource_use_permissions(
        army,
    )

    assert result == (
        OwnedResourceUsePermission(
            owner=ResourceOwner(
                profile_id="DG_NEC",
                instance_index=1,
            ),
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.TAKE_FATE,
        ),
    )


def test_repeated_models_receive_separate_owned_permissions():
    army = Army()

    army.add_profile(
        make_profile(
            "DG_SM",
            special_resource_permissions=(
                (
                    ResourceType.WILL,
                    ResourceUse.TAKE_FATE,
                ),
            ),
        ),
        quantity=2,
    )

    result = get_initial_owned_resource_use_permissions(
        army,
    )

    assert result == (
        OwnedResourceUsePermission(
            owner=ResourceOwner(
                profile_id="DG_SM",
                instance_index=1,
            ),
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.TAKE_FATE,
        ),
        OwnedResourceUsePermission(
            owner=ResourceOwner(
                profile_id="DG_SM",
                instance_index=2,
            ),
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.TAKE_FATE,
        ),
    )

def test_initial_permissions_include_profile_special_rule_semantics():
    rule = SpecialRule(
        id="UNHOLY_RESURRECTION",
        name="Unholy Resurrection",
        category=RuleCategory.SPECIAL,
    )

    profile = make_profile(
        "DG_NEC",
        special_rules=[
            ProfileSpecialRuleAssignment(
                rule=rule,
            ),
        ],
    )

    army = Army()
    army.add_profile(
        profile,
        quantity=1,
    )

    result = get_initial_owned_resource_use_permissions(
        army,
    )

    assert result == (
        OwnedResourceUsePermission(
            owner=ResourceOwner(
                profile_id="DG_NEC",
                instance_index=1,
            ),
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.BOOST_RESURRECTION,
        ),
    )
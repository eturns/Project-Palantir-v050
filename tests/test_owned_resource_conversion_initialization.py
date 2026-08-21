from army import Army
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from owned_resource_conversion_initialization import (
    get_initial_owned_resource_conversions,
)
from profiles import Profile
from resource_conversion import ResourceConversion
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
    special_resource_conversions: tuple[
        ResourceConversion,
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
        special_rules=(
            []
            if special_rules is None
            else special_rules
        ),
        special_resource_conversions=special_resource_conversions,
    )


def test_default_profile_initializes_with_no_special_conversions():
    army = Army()

    army.add_profile(
        make_profile("DG_WK"),
        quantity=1,
    )

    result = get_initial_owned_resource_conversions(
        army,
    )

    assert result == ()


def test_profile_declared_conversion_is_created_for_owner():
    army = Army()

    conversion = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    army.add_profile(
        make_profile(
            "DG_NEC",
            special_resource_conversions=(
                conversion,
            ),
        ),
        quantity=1,
    )

    result = get_initial_owned_resource_conversions(
        army,
    )

    assert result == (
        OwnedResourceConversion(
            owner=ResourceOwner(
                profile_id="DG_NEC",
                instance_index=1,
            ),
            conversion=conversion,
        ),
    )


def test_repeated_models_receive_separate_owned_conversions():
    army = Army()

    conversion = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    army.add_profile(
        make_profile(
            "DG_SM",
            special_resource_conversions=(
                conversion,
            ),
        ),
        quantity=2,
    )

    result = get_initial_owned_resource_conversions(
        army,
    )

    assert result == (
        OwnedResourceConversion(
            owner=ResourceOwner(
                profile_id="DG_SM",
                instance_index=1,
            ),
            conversion=conversion,
        ),
        OwnedResourceConversion(
            owner=ResourceOwner(
                profile_id="DG_SM",
                instance_index=2,
            ),
            conversion=conversion,
        ),
    )

def test_initial_conversions_include_profile_special_rule_semantics():
    rule = SpecialRule(
        id="HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
        name="He Cannot Yet Take Physical Form",
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

    result = get_initial_owned_resource_conversions(
        army,
    )

    assert result == (
        OwnedResourceConversion(
            owner=ResourceOwner(
                profile_id="DG_NEC",
                instance_index=1,
            ),
            conversion=ResourceConversion(
                source_resource_type=ResourceType.WILL,
                target_resource_use=ResourceUse.TAKE_FATE,
            ),
        ),
    )
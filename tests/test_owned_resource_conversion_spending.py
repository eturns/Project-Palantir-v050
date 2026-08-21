import pytest
from army import Army
from owned_resource_conversion_initialization import (
    get_initial_owned_resource_conversions,
)
from profiles import Profile
from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_conversion import OwnedResourceConversion
from owned_resource_conversion_spending import (
    apply_owned_resource_conversion_spend,
)
from resource_conversion import ResourceConversion
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def test_converted_will_spend_reduces_will_without_creating_fate():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    state = OwnedHeroResourceState(
        owner=owner,
        resources=HeroResourceState(
            remaining_might=3,
            remaining_will=25,
            remaining_fate=0,
        ),
    )

    conversion = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    owned_conversion = OwnedResourceConversion(
        owner=owner,
        conversion=conversion,
    )

    result = apply_owned_resource_conversion_spend(
        state=state,
        conversion=owned_conversion,
        amount=1,
    )

    assert result.owner == owner
    assert result.resources == HeroResourceState(
        remaining_might=3,
        remaining_will=24,
        remaining_fate=0,
    )


def test_converted_spend_does_not_mutate_original_state():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    state = OwnedHeroResourceState(
        owner=owner,
        resources=HeroResourceState(
            remaining_might=3,
            remaining_will=25,
            remaining_fate=0,
        ),
    )

    conversion = OwnedResourceConversion(
        owner=owner,
        conversion=ResourceConversion(
            source_resource_type=ResourceType.WILL,
            target_resource_use=ResourceUse.TAKE_FATE,
        ),
    )

    apply_owned_resource_conversion_spend(
        state=state,
        conversion=conversion,
        amount=1,
    )

    assert state.resources == HeroResourceState(
        remaining_might=3,
        remaining_will=25,
        remaining_fate=0,
    )


def test_conversion_cannot_be_spent_by_different_owner():
    state = OwnedHeroResourceState(
        owner=ResourceOwner(
            profile_id="DG_WK",
            instance_index=1,
        ),
        resources=HeroResourceState(
            remaining_might=3,
            remaining_will=10,
            remaining_fate=2,
        ),
    )

    conversion = OwnedResourceConversion(
        owner=ResourceOwner(
            profile_id="DG_NEC",
            instance_index=1,
        ),
        conversion=ResourceConversion(
            source_resource_type=ResourceType.WILL,
            target_resource_use=ResourceUse.TAKE_FATE,
        ),
    )

    with pytest.raises(
        ValueError,
        match="Resource conversion owner does not match resource state owner.",
    ):
        apply_owned_resource_conversion_spend(
            state=state,
            conversion=conversion,
            amount=1,
        )

def make_profile_with_special_conversion(
    profile_id: str,
    conversion: ResourceConversion,
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
        might=3,
        will=25,
        fate=0,
        max_in_army=0,
        special_resource_conversions=(
            conversion,
        ),
    )


def test_profile_declared_conversion_can_be_applied_end_to_end():
    conversion = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    army = Army()

    army.add_profile(
        make_profile_with_special_conversion(
            profile_id="DG_NEC",
            conversion=conversion,
        ),
        quantity=1,
    )

    conversions = get_initial_owned_resource_conversions(
        army,
    )

    state = OwnedHeroResourceState(
        owner=ResourceOwner(
            profile_id="DG_NEC",
            instance_index=1,
        ),
        resources=HeroResourceState(
            remaining_might=3,
            remaining_will=25,
            remaining_fate=0,
        ),
    )

    result = apply_owned_resource_conversion_spend(
        state=state,
        conversion=conversions[0],
        amount=1,
    )

    assert result.resources == HeroResourceState(
        remaining_might=3,
        remaining_will=24,
        remaining_fate=0,
    )
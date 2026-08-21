from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_endurance import (
    calculate_owned_resource_endurance,
)
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)
from battle_length_assumption import BattleHorizon
from resource_owner import ResourceOwner
from resource_strategy import ResourceStrategy
from owned_resource_conversion import OwnedResourceConversion
from owned_resource_use_permission import OwnedResourceUsePermission
from resource_conversion import ResourceConversion
from resource_use import ResourceUse
from resource_use_permission import ResourceType

def test_owned_resource_endurance_scores_each_owner_resource_pool():
    states = (
        OwnedHeroResourceState(
            owner=ResourceOwner(
                profile_id="DG_NEC",
                instance_index=1,
            ),
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=25,
                remaining_fate=0,
            ),
        ),
        OwnedHeroResourceState(
            owner=ResourceOwner(
                profile_id="DG_WK",
                instance_index=1,
            ),
            resources=HeroResourceState(
                remaining_might=2,
                remaining_will=3,
                remaining_fate=1,
            ),
        ),
    )

    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    result = calculate_owned_resource_endurance(
        states=states,
        assumption=assumption,
    )

    assert 0.0 <= result <= 1.0


def test_owned_resource_endurance_returns_zero_without_resources():
    states = (
        OwnedHeroResourceState(
            owner=ResourceOwner(
                profile_id="DG_MGS",
                instance_index=1,
            ),
            resources=HeroResourceState(),
        ),
    )

    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    assert (
        calculate_owned_resource_endurance(
            states=states,
            assumption=assumption,
        )
        == 0.0
    )

def test_extra_legal_uses_do_not_duplicate_same_resource_pool():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    states = (
        OwnedHeroResourceState(
            owner=owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=25,
                remaining_fate=0,
            ),
        ),
    )

    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    baseline = calculate_owned_resource_endurance(
        states=states,
        assumption=assumption,
        permissions=(),
        conversions=(),
    )

    with_semantics = calculate_owned_resource_endurance(
        states=states,
        assumption=assumption,
        permissions=(
            OwnedResourceUsePermission(
                owner=owner,
                resource_type=ResourceType.WILL,
                resource_use=ResourceUse.BOOST_RESURRECTION,
            ),
        ),
        conversions=(
            OwnedResourceConversion(
                owner=owner,
                conversion=ResourceConversion(
                    source_resource_type=ResourceType.WILL,
                    target_resource_use=ResourceUse.TAKE_FATE,
                ),
            ),
        ),
    )

    assert with_semantics == baseline
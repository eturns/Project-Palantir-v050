from hero_resource_spending import spend_will
from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from resource_owner import ResourceOwner


def test_spending_one_owners_resources_does_not_change_another_owner():
    necromancer = OwnedHeroResourceState(
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

    witch_king = OwnedHeroResourceState(
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

    updated_necromancer_resources = spend_will(
        necromancer.resources,
        amount=1,
    )

    updated_necromancer = OwnedHeroResourceState(
        owner=necromancer.owner,
        resources=updated_necromancer_resources,
    )

    assert updated_necromancer.resources.remaining_will == 24
    assert witch_king.resources.remaining_will == 10
    assert updated_necromancer.owner == necromancer.owner
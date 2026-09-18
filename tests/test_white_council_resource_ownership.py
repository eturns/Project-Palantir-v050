from army import Army
from owned_army_resource_initialization import (
    get_initial_owned_hero_resource_states,
)
from profiles import Profile
from hero_resource_spending import spend_will
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_allocation_application import (
    apply_owned_resource_allocations,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType

def make_white_council_profile(
    profile_id: str,
    will: int,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=0,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=3,
        courage="3+",
        intelligence="3+",
        might=3,
        will=will,
        fate=3,
        max_in_army=1,
    )


def test_white_council_casters_get_distinct_resource_owners():
    army = Army()

    profiles = (
        make_white_council_profile(
            "SARUMAN_THE_WHITE",
            will=6,
        ),
        make_white_council_profile(
            "GANDALF_THE_GREY",
            will=6,
        ),
        make_white_council_profile(
            "RADAGAST_THE_BROWN",
            will=6,
        ),
        make_white_council_profile(
            "GALADRIEL_LADY_OF_LIGHT",
            will=6,
        ),
        make_white_council_profile(
            "ELROND_MASTER_OF_RIVENDELL",
            will=3,
        ),
    )

    for profile in profiles:
        army.add_profile(
            profile,
            quantity=1,
            warband_id="WHITE_COUNCIL",
        )

    states = get_initial_owned_hero_resource_states(
        army,
    )

    assert len(states) == 5

    owner_ids = {
        state.owner.fielded_model_id
        for state in states
    }

    assert len(owner_ids) == 5

    assert sorted(
        state.resources.remaining_will
        for state in states
    ) == [3, 6, 6, 6, 6]

def test_white_council_will_spending_is_isolated_by_owner():
    army = Army()

    profiles = (
        make_white_council_profile(
            "SARUMAN_THE_WHITE",
            will=6,
        ),
        make_white_council_profile(
            "GANDALF_THE_GREY",
            will=6,
        ),
        make_white_council_profile(
            "RADAGAST_THE_BROWN",
            will=6,
        ),
        make_white_council_profile(
            "GALADRIEL_LADY_OF_LIGHT",
            will=6,
        ),
        make_white_council_profile(
            "ELROND_MASTER_OF_RIVENDELL",
            will=3,
        ),
    )

    for profile in profiles:
        army.add_profile(
            profile,
            quantity=1,
            warband_id="WHITE_COUNCIL",
        )

    states = get_initial_owned_hero_resource_states(
        army,
    )

    saruman = next(
        state
        for state in states
        if state.owner.fielded_model_id.startswith(
            "SARUMAN_THE_WHITE:"
        )
    )

    updated_saruman = OwnedHeroResourceState(
        owner=saruman.owner,
        resources=spend_will(
            saruman.resources,
            amount=2,
        ),
    )

    assert updated_saruman.resources.remaining_will == 4

    unchanged_states = tuple(
        state
        for state in states
        if state.owner != saruman.owner
    )

    assert sorted(
        state.resources.remaining_will
        for state in unchanged_states
    ) == [3, 6, 6, 6]

def test_white_council_multiple_casters_can_spend_independently():
    army = Army()

    profiles = (
        make_white_council_profile(
            "SARUMAN_THE_WHITE",
            will=6,
        ),
        make_white_council_profile(
            "GANDALF_THE_GREY",
            will=6,
        ),
        make_white_council_profile(
            "RADAGAST_THE_BROWN",
            will=6,
        ),
        make_white_council_profile(
            "GALADRIEL_LADY_OF_LIGHT",
            will=6,
        ),
        make_white_council_profile(
            "ELROND_MASTER_OF_RIVENDELL",
            will=3,
        ),
    )

    for profile in profiles:
        army.add_profile(
            profile,
            quantity=1,
            warband_id="WHITE_COUNCIL",
        )

    states = get_initial_owned_hero_resource_states(
        army,
    )

    saruman = next(
        state
        for state in states
        if state.owner.fielded_model_id.startswith(
            "SARUMAN_THE_WHITE:"
        )
    )

    gandalf = next(
        state
        for state in states
        if state.owner.fielded_model_id.startswith(
            "GANDALF_THE_GREY:"
        )
    )

    allocations = (
        OwnedResourceAllocation(
            owner=saruman.owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=2,
        ),
        OwnedResourceAllocation(
            owner=gandalf.owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=1,
        ),
    )

    updated_states = apply_owned_resource_allocations(
        states=states,
        allocations=allocations,
        permissions=(),
        conversions=(),
    )

    will_by_profile = {
        state.owner.fielded_model_id.split(":")[0]:
        state.resources.remaining_will
        for state in updated_states
    }

    assert will_by_profile["SARUMAN_THE_WHITE"] == 4
    assert will_by_profile["GANDALF_THE_GREY"] == 5
    assert will_by_profile["RADAGAST_THE_BROWN"] == 6
    assert will_by_profile["GALADRIEL_LADY_OF_LIGHT"] == 6
    assert will_by_profile["ELROND_MASTER_OF_RIVENDELL"] == 3

def test_white_council_all_casters_keep_independent_will_pools():
    army = Army()

    profiles = (
        make_white_council_profile(
            "SARUMAN_THE_WHITE",
            will=6,
        ),
        make_white_council_profile(
            "GANDALF_THE_GREY",
            will=6,
        ),
        make_white_council_profile(
            "RADAGAST_THE_BROWN",
            will=6,
        ),
        make_white_council_profile(
            "GALADRIEL_LADY_OF_LIGHT",
            will=6,
        ),
        make_white_council_profile(
            "ELROND_MASTER_OF_RIVENDELL",
            will=3,
        ),
    )

    for profile in profiles:
        army.add_profile(
            profile,
            quantity=1,
            warband_id="WHITE_COUNCIL",
        )

    states = get_initial_owned_hero_resource_states(
        army,
    )

    states_by_profile = {
        state.owner.fielded_model_id.split(":")[0]:
        state
        for state in states
    }

    allocations = (
        OwnedResourceAllocation(
            owner=states_by_profile[
                "SARUMAN_THE_WHITE"
            ].owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=1,
        ),
        OwnedResourceAllocation(
            owner=states_by_profile[
                "GANDALF_THE_GREY"
            ].owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=2,
        ),
        OwnedResourceAllocation(
            owner=states_by_profile[
                "RADAGAST_THE_BROWN"
            ].owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=3,
        ),
        OwnedResourceAllocation(
            owner=states_by_profile[
                "GALADRIEL_LADY_OF_LIGHT"
            ].owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=4,
        ),
        OwnedResourceAllocation(
            owner=states_by_profile[
                "ELROND_MASTER_OF_RIVENDELL"
            ].owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=2,
        ),
    )

    updated_states = apply_owned_resource_allocations(
        states=states,
        allocations=allocations,
        permissions=(),
        conversions=(),
    )

    remaining_will = {
        state.owner.fielded_model_id.split(":")[0]:
        state.resources.remaining_will
        for state in updated_states
    }

    assert remaining_will == {
        "SARUMAN_THE_WHITE": 5,
        "GANDALF_THE_GREY": 4,
        "RADAGAST_THE_BROWN": 3,
        "GALADRIEL_LADY_OF_LIGHT": 2,
        "ELROND_MASTER_OF_RIVENDELL": 1,
    }
from resource_owner import ResourceOwner
from resource_use_permission import ResourceType
from special_rule_temporary_resource_grants import (
    get_special_rule_temporary_resource_grants,
)
from bringer_of_death_state import (
    BringerOfDeathState,
)
from configured_profile import ConfiguredProfile
from effective_special_rule_ids import (
    get_effective_special_rule_ids,
)
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from hero_resource_state import HeroResourceState
from owned_hero_resource_state import (
    OwnedHeroResourceState,
)
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_turn_transition import (
    apply_owned_resource_turn,
)
from resource_use import ResourceUse

def make_bolg() -> ConfiguredProfile:
    profile = Profile(
        id="BOLG_SPAWN_OF_AZOG",
        name="Bolg, Spawn of Azog",
        points=175,
        movement=6,
        fight=7,
        shooting="4+",
        strength=5,
        defence=7,
        attacks=3,
        wounds=3,
        courage="5+",
        intelligence="5+",
        might=3,
        will=3,
        fate=1,
        max_in_army=1,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="BRINGER_OF_DEATH",
                name="The Bringer of Death",
                category=RuleCategory.SPECIAL,
            ),
        )
    )

    return ConfiguredProfile(
        profile=profile,
    )

def test_mighty_hero_grants_one_temporary_might():
    owner = ResourceOwner(
        fielded_model_id="BOLG:1:1",
    )

    grants = (
        get_special_rule_temporary_resource_grants(
            owner=owner,
            rule_ids=frozenset(
                {"MIGHTY_HERO"}
            ),
        )
    )

    assert len(grants) == 1
    assert grants[0].owner == owner
    assert (
        grants[0].resource_type
        == ResourceType.MIGHT
    )
    assert grants[0].amount == 1

def test_bringers_mighty_hero_runtime_rule_produces_temporary_might():
    owner = ResourceOwner(
        fielded_model_id="BOLG:1:1",
    )

    bolg = make_bolg()

    rule_ids = get_effective_special_rule_ids(
        bolg,
        bringer_of_death_state=BringerOfDeathState(
            kills_in_combat=8,
        ),
    )

    grants = (
        get_special_rule_temporary_resource_grants(
            owner=owner,
            rule_ids=rule_ids,
        )
    )

    assert len(grants) == 1
    assert grants[0].resource_type == ResourceType.MIGHT
    assert grants[0].amount == 1

def test_bringers_mighty_hero_is_not_granted_before_eight_kills():
    owner = ResourceOwner(
        fielded_model_id="BOLG:1:1",
    )

    bolg = make_bolg()

    rule_ids = get_effective_special_rule_ids(
        bolg,
        bringer_of_death_state=BringerOfDeathState(
            kills_in_combat=7,
        ),
    )

    grants = (
        get_special_rule_temporary_resource_grants(
            owner=owner,
            rule_ids=rule_ids,
        )
    )

    assert grants == ()

def test_bringers_mighty_hero_temporary_might_is_spent_before_normal_might():
    owner = ResourceOwner(
        fielded_model_id="BOLG:1:1",
    )

    bolg = make_bolg()

    rule_ids = get_effective_special_rule_ids(
        bolg,
        bringer_of_death_state=BringerOfDeathState(
            kills_in_combat=8,
        ),
    )

    temporary_grants = (
        get_special_rule_temporary_resource_grants(
            owner=owner,
            rule_ids=rule_ids,
        )
    )

    states = (
        OwnedHeroResourceState(
            owner=owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=3,
                remaining_fate=1,
            ),
        ),
    )

    result = apply_owned_resource_turn(
        states=states,
        allocations=(
            OwnedResourceAllocation(
                owner=owner,
                resource_type=ResourceType.MIGHT,
                resource_use=ResourceUse.MODIFY_DUEL,
                amount=1,
            ),
        ),
        permissions=(),
        conversions=(),
        temporary_grants=temporary_grants,
    )

    assert result[0].resources.remaining_might == 3
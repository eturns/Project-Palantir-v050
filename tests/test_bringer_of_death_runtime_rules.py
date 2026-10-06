from bringer_of_death_state import (
    BringerOfDeathState,
)
from bringer_of_death_runtime_rules import (
    get_bringer_of_death_runtime_rule_ids,
)
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from effective_special_rule_ids import (
    get_effective_special_rule_ids,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from bringer_of_death_runtime_rules import (
    get_bringer_of_death_runtime_rule_assignments,
    get_bringer_of_death_runtime_rule_ids,
)

def test_bringer_of_death_has_no_runtime_rules_before_two_kills():
    assert get_bringer_of_death_runtime_rule_ids(
        BringerOfDeathState(
            kills_in_combat=1,
        )
    ) == frozenset()


def test_bringer_of_death_gains_terror_at_two_kills():
    assert get_bringer_of_death_runtime_rule_ids(
        BringerOfDeathState(
            kills_in_combat=2,
        )
    ) == frozenset(
        {
            "TERROR",
        }
    )


def test_bringer_of_death_gains_harbinger_at_five_kills():
    assert get_bringer_of_death_runtime_rule_ids(
        BringerOfDeathState(
            kills_in_combat=5,
        )
    ) == frozenset(
        {
            "TERROR",
            "HARBINGER_OF_EVIL",
        }
    )


def test_bringer_of_death_gains_mighty_hero_at_eight_kills():
    assert get_bringer_of_death_runtime_rule_ids(
        BringerOfDeathState(
            kills_in_combat=8,
        )
    ) == frozenset(
        {
            "TERROR",
            "HARBINGER_OF_EVIL",
            "MIGHTY_HERO",
        }
    )

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


def test_bring_of_death_runtime_rules_flow_through_effective_rules():
    bolg = make_bolg()

    rule_ids = get_effective_special_rule_ids(
        bolg,
        bringer_of_death_state=(
            BringerOfDeathState(
                kills_in_combat=8,
            )
        ),
    )

    assert {
        "BRINGER_OF_DEATH",
        "TERROR",
        "HARBINGER_OF_EVIL",
        "MIGHTY_HERO",
    }.issubset(
        rule_ids
    )

def test_bringer_of_death_harbinger_has_twelve_inch_parameter():
    assignments = (
        get_bringer_of_death_runtime_rule_assignments(
            BringerOfDeathState(
                kills_in_combat=5,
            )
        )
    )

    harbinger = next(
        assignment
        for assignment in assignments
        if assignment.rule_id
        == "HARBINGER_OF_EVIL"
    )

    assert harbinger.parameter == 12


def test_bringer_of_death_eight_kills_preserves_all_runtime_assignments():
    assignments = (
        get_bringer_of_death_runtime_rule_assignments(
            BringerOfDeathState(
                kills_in_combat=8,
            )
        )
    )

    assert {
        assignment.rule_id
        for assignment in assignments
    } == {
        "TERROR",
        "HARBINGER_OF_EVIL",
        "MIGHTY_HERO",
    }

    assert next(
        assignment.parameter
        for assignment in assignments
        if assignment.rule_id
        == "HARBINGER_OF_EVIL"
    ) == 12
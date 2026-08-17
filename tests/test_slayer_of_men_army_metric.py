import pytest

from army import Army
from army_list import ArmyList
from faction import Faction
from profiles import Profile

from ability_tag_entity import AbilityTagEntity
from ability_tag_assignment import AbilityTagAssignment
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule

from army_metrics import calculate_army_metrics


def make_slayer() -> Profile:
    slayer = Profile(
        id="DG_SM",
        name="The Slayer of Men",
        points=80,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=2,
        base_size_mm=25,
    )

    hero_hunting_tag = AbilityTagEntity(
        id="HERO_HUNTING",
        name="Hero Hunting",
    )

    angmar_arise = SpecialRule(
        id="ANGMAR_ARISE_SOM",
        name="Angmar Arise",
        category=RuleCategory.OFFENCE,
    )

    angmar_arise.ability_tags.append(
        AbilityTagAssignment(
            tag=hero_hunting_tag,
            weight=1.75,
        )
    )

    slayer.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=angmar_arise,
        )
    )

    return slayer


def make_army_list() -> ArmyList:
    return ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=Faction(
            id="TEST_FACTION",
            name="Test Faction",
        ),
    )


def test_single_slayer_has_no_paired_burly_offence_bonus():
    army = Army()

    army.add_profile(
        make_slayer(),
        quantity=1,
    )

    metrics = calculate_army_metrics(
        army,
        make_army_list(),
    )

    assert metrics.offence == pytest.approx(
        0.0,
    )

    assert metrics.hero_hunting == pytest.approx(
        1.75,
    )


def test_two_slayers_gain_one_paired_burly_offence_bonus():
    army = Army()

    army.add_profile(
        make_slayer(),
        quantity=2,
    )

    metrics = calculate_army_metrics(
        army,
        make_army_list(),
    )

    assert metrics.offence == pytest.approx(
        0.5,
    )

    assert metrics.hero_hunting == pytest.approx(
        3.5,
    )
import pytest

import board_presence_input_builder

from army import Army
from army_list import ArmyList
from army_metrics_entity import ArmyMetrics
from faction import Faction
from profiles import Profile
from ability_tag_entity import AbilityTagEntity
from ability_tag_assignment import AbilityTagAssignment
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule

def make_profile() -> Profile:
    return Profile(
        id="TEST",
        name="Test Profile",
        points=10,
        movement=6,
        fight=3,
        shooting="4+",
        strength=3,
        defence=3,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        base_size_mm=25,
    )


def test_build_board_presence_inputs_normalises_army_values(
    monkeypatch,
):
    army = Army()

    army.add_profile(
        make_profile(),
        quantity=5,
    )

    army_list = ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=Faction(
            id="TEST_FACTION",
            name="Test Faction",
        ),
    )

    monkeypatch.setattr(
        board_presence_input_builder,
        "calculate_army_metric_densities",
        lambda army, army_list: ArmyMetrics(
            control=2.5,
        ),
    )

    inputs = (
        board_presence_input_builder
        .build_board_presence_inputs(
            army,
            army_list,
        )
    )

    assert inputs.model_presence == pytest.approx(
        1.0,
    )

    assert inputs.manoeuvrability == pytest.approx(
        0.6,
    )

    assert inputs.control == pytest.approx(
        0.5,
    )

def test_build_board_presence_inputs_includes_mobility_rule_in_manoeuvrability(
    monkeypatch,
):
    army = Army()

    profile = make_profile()

    mobility_tag = AbilityTagEntity(
        id="MOBILITY",
        name="Mobility",
    )

    unnatural_speed = SpecialRule(
        id="UNNATURAL_SPEED",
        name="Unnatural Speed",
        category=RuleCategory.MOBILITY,
    )

    unnatural_speed.ability_tags.append(
        AbilityTagAssignment(
            tag=mobility_tag,
            weight=1.5,
        )
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=unnatural_speed,
        )
    )

    army.add_profile(
        profile,
    )

    army_list = ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=Faction(
            id="TEST_FACTION",
            name="Test Faction",
        ),
    )

    monkeypatch.setattr(
        board_presence_input_builder,
        "calculate_army_metric_densities",
        lambda army, army_list: ArmyMetrics(
            control=0.0,
        ),
    )

    inputs = (
        board_presence_input_builder
        .build_board_presence_inputs(
            army,
            army_list,
        )
    )

    assert inputs.manoeuvrability == pytest.approx(
        0.75,
    )
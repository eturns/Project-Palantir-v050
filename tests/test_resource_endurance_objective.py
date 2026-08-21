import pytest

import resource_endurance_objective

from army import Army
from battle_length_assumption import BattleHorizon
from optimiser_candidate import OptimiserCandidate
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)
from resource_endurance_objective import (
    ResourceEnduranceObjective,
)
from resource_strategy import ResourceStrategy

from army_resource_state import ArmyResourceState
from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from resource_owner import ResourceOwner

def test_resource_endurance_objective_evaluates_candidate(
    monkeypatch,
):
    army = Army()

    candidate = OptimiserCandidate(
        army=army,
    )

    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    resources = ArmyResourceState(
        might=4,
        will=4,
        fate=4,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_totals",
        lambda army: resources,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_trajectory",
        lambda resources, assumption: "TRAJECTORY",
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_endurance",
        lambda resources, trajectory: 0.72,
    )
    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_resource_capacity_score",
        lambda might, will, fate, army_points: 0.72,
    )

    objective = ResourceEnduranceObjective(
        assumption=assumption,
    )

    score = objective.evaluate(
        candidate,
    )

    assert score == pytest.approx(0.72)

def test_more_might_improves_resource_endurance_for_same_army_points(
    monkeypatch,
):
    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    lower_army = Army()
    higher_army = Army()

    lower_candidate = OptimiserCandidate(
        army=lower_army,
    )

    higher_candidate = OptimiserCandidate(
        army=higher_army,
    )

    resource_totals = {
        id(lower_army): ArmyResourceState(
            might=8,
            will=30,
            fate=0,
        ),
        id(higher_army): ArmyResourceState(
            might=10,
            will=30,
            fate=0,
        ),
    }

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_totals",
        lambda army: resource_totals[id(army)],
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_trajectory",
        lambda resources, assumption: (
            "LOWER_TRAJECTORY"
            if resources.might == 8
            else "HIGHER_TRAJECTORY"
        ),
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_endurance",
        lambda resources, trajectory: (
            0.9825
            if resources.might == 8
            else 0.9300
        ),
    )

    monkeypatch.setattr(
        lower_army,
        "total_points",
        lambda: 700,
    )

    monkeypatch.setattr(
        higher_army,
        "total_points",
        lambda: 700,
    )

    objective = ResourceEnduranceObjective(
        assumption=assumption,
    )

    lower_score = objective.evaluate(
        lower_candidate,
    )

    higher_score = objective.evaluate(
        higher_candidate,
    )

    assert higher_score > lower_score

def test_more_will_improves_resource_endurance_for_same_army_points(
    monkeypatch,
):
    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    lower_army = Army()
    higher_army = Army()

    lower_candidate = OptimiserCandidate(
        army=lower_army,
    )

    higher_candidate = OptimiserCandidate(
        army=higher_army,
    )

    resource_totals = {
        id(lower_army): ArmyResourceState(
            might=8,
            will=8,
            fate=0,
        ),
        id(higher_army): ArmyResourceState(
            might=8,
            will=10,
            fate=0,
        ),
    }

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_totals",
        lambda army: resource_totals[id(army)],
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_trajectory",
        lambda resources, assumption: (
            "LOWER_TRAJECTORY"
            if resources.will == 8
            else "HIGHER_TRAJECTORY"
        ),
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_endurance",
        lambda resources, trajectory: (
            0.98
            if resources.will == 8
            else 0.93
        ),
    )

    monkeypatch.setattr(
        lower_army,
        "total_points",
        lambda: 700,
    )

    monkeypatch.setattr(
        higher_army,
        "total_points",
        lambda: 700,
    )

    objective = ResourceEnduranceObjective(
        assumption=assumption,
    )

    lower_score = objective.evaluate(
        lower_candidate,
    )

    higher_score = objective.evaluate(
        higher_candidate,
    )

    assert higher_score > lower_score


def test_more_fate_improves_resource_endurance_for_same_army_points(
    monkeypatch,
):
    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    lower_army = Army()
    higher_army = Army()

    lower_candidate = OptimiserCandidate(
        army=lower_army,
    )

    higher_candidate = OptimiserCandidate(
        army=higher_army,
    )

    resource_totals = {
        id(lower_army): ArmyResourceState(
            might=8,
            will=8,
            fate=1,
        ),
        id(higher_army): ArmyResourceState(
            might=8,
            will=8,
            fate=2,
        ),
    }

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_totals",
        lambda army: resource_totals[id(army)],
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_trajectory",
        lambda resources, assumption: (
            "LOWER_TRAJECTORY"
            if resources.fate == 1
            else "HIGHER_TRAJECTORY"
        ),
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_endurance",
        lambda resources, trajectory: (
            0.98
            if resources.fate == 1
            else 0.93
        ),
    )

    monkeypatch.setattr(
        lower_army,
        "total_points",
        lambda: 700,
    )

    monkeypatch.setattr(
        higher_army,
        "total_points",
        lambda: 700,
    )

    objective = ResourceEnduranceObjective(
        assumption=assumption,
    )

    lower_score = objective.evaluate(
        lower_candidate,
    )

    higher_score = objective.evaluate(
        higher_candidate,
    )

    assert higher_score > lower_score

def test_resource_endurance_objective_uses_owned_resource_management(
    monkeypatch,
):
    army = Army()

    candidate = OptimiserCandidate(
        army=army,
    )

    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    resources = ArmyResourceState(
        might=3,
        will=25,
        fate=0,
    )

    owned_states = (
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
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_totals",
        lambda army: resources,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "get_initial_owned_hero_resource_states",
        lambda army: owned_states,
        raising=False,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_owned_resource_endurance",
        lambda states, assumption, permissions, conversions: 0.80,
        raising=False,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_resource_capacity_score",
        lambda might, will, fate, army_points: 0.60,
    )

    monkeypatch.setattr(
        army,
        "total_points",
        lambda: 700,
    )

    objective = ResourceEnduranceObjective(
        assumption=assumption,
    )

    score = objective.evaluate(
        candidate,
    )

    assert score == pytest.approx(
        0.60 * 0.55
        + 0.80 * 0.45
    )

def test_resource_endurance_objective_initializes_owned_resource_semantics(
    monkeypatch,
):
    army = Army()

    candidate = OptimiserCandidate(
        army=army,
    )

    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    resources = ArmyResourceState(
        might=3,
        will=25,
        fate=0,
    )

    owned_states = (
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
    )

    calls = {
        "permissions": False,
        "conversions": False,
    }

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_totals",
        lambda army: resources,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "get_initial_owned_hero_resource_states",
        lambda army: owned_states,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "get_initial_owned_resource_use_permissions",
        lambda army: calls.__setitem__(
            "permissions",
            True,
        ) or (),
        raising=False,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "get_initial_owned_resource_conversions",
        lambda army: calls.__setitem__(
            "conversions",
            True,
        ) or (),
        raising=False,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_owned_resource_endurance",
        lambda states, assumption, permissions, conversions: 0.60,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_resource_capacity_score",
        lambda might, will, fate, army_points: 0.60,
    )

    monkeypatch.setattr(
        army,
        "total_points",
        lambda: 700,
    )

    objective = ResourceEnduranceObjective(
        assumption=assumption,
    )

    objective.evaluate(
        candidate,
    )

    assert calls["permissions"] is True
    assert calls["conversions"] is True

def test_resource_endurance_passes_owned_semantics_to_management(
    monkeypatch,
):
    army = Army()

    candidate = OptimiserCandidate(
        army=army,
    )

    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    resources = ArmyResourceState(
        might=3,
        will=25,
        fate=0,
    )

    owned_states = (
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
    )

    owned_permissions = ("PERMISSION",)
    owned_conversions = ("CONVERSION",)

    received = {}

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_totals",
        lambda army: resources,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "get_initial_owned_hero_resource_states",
        lambda army: owned_states,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "get_initial_owned_resource_use_permissions",
        lambda army: owned_permissions,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "get_initial_owned_resource_conversions",
        lambda army: owned_conversions,
    )

    def fake_owned_resource_endurance(
        states,
        assumption,
        permissions,
        conversions,
    ):
        received["states"] = states
        received["permissions"] = permissions
        received["conversions"] = conversions
        return 0.60

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_owned_resource_endurance",
        fake_owned_resource_endurance,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_resource_capacity_score",
        lambda might, will, fate, army_points: 0.60,
    )

    monkeypatch.setattr(
        army,
        "total_points",
        lambda: 700,
    )

    objective = ResourceEnduranceObjective(
        assumption=assumption,
    )

    objective.evaluate(
        candidate,
    )

    assert received["states"] == owned_states
    assert received["permissions"] == owned_permissions
    assert received["conversions"] == owned_conversions
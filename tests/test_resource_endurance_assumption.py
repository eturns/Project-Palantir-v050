from battle_length_assumption import BattleHorizon
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)
from resource_strategy import ResourceStrategy


def test_resource_endurance_assumption_stores_explicit_horizon_and_strategy():
    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    assert assumption.horizon == BattleHorizon.MEDIUM
    assert assumption.strategy == ResourceStrategy.BALANCED
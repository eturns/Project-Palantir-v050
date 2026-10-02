from torturer_runtime_rules import (
    get_torturer_runtime_rule_ids,
)
from torturer_state import TorturerState


def test_torturer_has_no_runtime_rule_before_three_kills():
    assert get_torturer_runtime_rule_ids(
        TorturerState(
            kills_in_combat=2,
        )
    ) == frozenset()


def test_torturer_gains_terror_at_three_kills():
    assert get_torturer_runtime_rule_ids(
        TorturerState(
            kills_in_combat=3,
        )
    ) == frozenset(
        {
            "TERROR",
        }
    )


def test_torturer_keeps_terror_above_three_kills():
    assert get_torturer_runtime_rule_ids(
        TorturerState(
            kills_in_combat=5,
        )
    ) == frozenset(
        {
            "TERROR",
        }
    )
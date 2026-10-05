from shattered_spirit_state import (
    ShatteredSpiritResult,
    ShatteredSpiritState,
)
from targeting_eligibility import (
    TargetingSource,
    can_target_model,
)


def opponent_controlled_state():
    return ShatteredSpiritState(
        result=ShatteredSpiritResult.OPPONENT_CONTROLLED,
    )


def normal_state():
    return ShatteredSpiritState(
        result=ShatteredSpiritResult.NORMAL,
    )


def test_normal_thrain_can_be_targeted():
    assert can_target_model(
        targeting_source=TargetingSource.SHOOTING,
        shattered_spirit_state=normal_state(),
    ) is True


def test_opponent_controlled_thrain_cannot_be_shot():
    assert can_target_model(
        targeting_source=TargetingSource.SHOOTING,
        shattered_spirit_state=opponent_controlled_state(),
    ) is False


def test_opponent_controlled_thrain_cannot_be_targeted_by_magical_power():
    assert can_target_model(
        targeting_source=TargetingSource.MAGICAL_POWER,
        shattered_spirit_state=opponent_controlled_state(),
    ) is False


def test_opponent_controlled_thrain_cannot_be_targeted_by_enemy_special_rule():
    assert can_target_model(
        targeting_source=TargetingSource.ENEMY_SPECIAL_RULE,
        shattered_spirit_state=opponent_controlled_state(),
    ) is False


def test_good_thrain_cannot_be_struck_by_good_model_when_opponent_controlled():
    assert can_target_model(
        targeting_source=TargetingSource.COMBAT_STRIKE,
        shattered_spirit_state=opponent_controlled_state(),
        target_is_good=True,
        source_is_good=True,
    ) is False


def test_good_thrain_cannot_be_used_as_in_the_way_for_good_shot():
    assert can_target_model(
        targeting_source=TargetingSource.IN_THE_WAY,
        shattered_spirit_state=opponent_controlled_state(),
        target_is_good=True,
        source_is_good=True,
    ) is False


def test_evil_source_can_still_strike_good_thrain():
    assert can_target_model(
        targeting_source=TargetingSource.COMBAT_STRIKE,
        shattered_spirit_state=opponent_controlled_state(),
        target_is_good=True,
        source_is_good=False,
    ) is True


def test_non_shattered_model_has_no_restriction():
    assert can_target_model(
        targeting_source=TargetingSource.MAGICAL_POWER,
    ) is True
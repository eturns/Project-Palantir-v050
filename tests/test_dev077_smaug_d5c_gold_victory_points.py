"""DEV-077-SMAUG-D5C: isolated end-game Gold Marker VP acceptance."""
import pytest
from smaug_gold_markers import deploy_gold_markers, kill_gold_carrier
from smaug_gold_victory_points import calculate_smaug_gold_victory_points


def initial():
    return deploy_gold_markers(('A','B','C'), smaug_model_id='SMAUG:1:1')


def recovered(n):
    state=initial()
    for i, carrier in enumerate(('A','B','C')[:n], 1):
        state=kill_gold_carrier(state, marker_id=f'GOLD_{i}', slain_model_id=carrier,
                                killed_by_smaug_in_combat=True)
    return state


def dropped(n):
    state=initial()
    for i, carrier in enumerate(('A','B','C')[:n], 1):
        state=kill_gold_carrier(state, marker_id=f'GOLD_{i}', slain_model_id=carrier,
                                killed_by_smaug_in_combat=False)
    return state


def test_all_three_recovered_awards_smaug_two():
    result=calculate_smaug_gold_victory_points(recovered(3),smaug_points=10,opponent_points=5)
    assert (result.smaug_bonus,result.opponent_bonus)==(2,0)
    assert (result.smaug_points_after,result.opponent_points_after)==(12,5)


def test_any_carried_awards_opponent_two():
    result=calculate_smaug_gold_victory_points(recovered(2),smaug_points=5,opponent_points=10)
    assert (result.smaug_bonus,result.opponent_bonus)==(0,2)
    assert (result.smaug_points_after,result.opponent_points_after)==(5,12)


def test_all_dropped_awards_nobody():
    result=calculate_smaug_gold_victory_points(dropped(3),smaug_points=3,opponent_points=7)
    assert (result.smaug_bonus,result.opponent_bonus)==(0,0)


def test_mix_recovered_and_dropped_awards_nobody():
    state=recovered(1)
    for i,carrier in ((2,'B'),(3,'C')):
        state=kill_gold_carrier(state,marker_id=f'GOLD_{i}',slain_model_id=carrier,
                                killed_by_smaug_in_combat=False)
    result=calculate_smaug_gold_victory_points(state,smaug_points=3,opponent_points=7)
    assert (result.smaug_bonus,result.opponent_bonus)==(0,0)


def test_all_initially_carried_awards_opponent():
    result=calculate_smaug_gold_victory_points(initial(),smaug_points=0,opponent_points=0)
    assert (result.smaug_bonus,result.opponent_bonus)==(0,2)


@pytest.mark.parametrize('points,bonus', [(0,2),(18,2),(19,1),(20,0)])
def test_smaug_twenty_point_cap(points,bonus):
    result=calculate_smaug_gold_victory_points(recovered(3),smaug_points=points,opponent_points=0)
    assert result.smaug_bonus==bonus
    assert result.smaug_points_after<=20


@pytest.mark.parametrize('points,bonus', [(0,2),(18,2),(19,1),(20,0)])
def test_opponent_twenty_point_cap(points,bonus):
    result=calculate_smaug_gold_victory_points(initial(),smaug_points=0,opponent_points=points)
    assert result.opponent_bonus==bonus
    assert result.opponent_points_after<=20


@pytest.mark.parametrize('bad', [-1,21,True,3.1,'5',None])
def test_invalid_victory_point_values_rejected(bad):
    with pytest.raises(ValueError):
        calculate_smaug_gold_victory_points(initial(),smaug_points=bad,opponent_points=0)


def test_invalid_state_rejected():
    with pytest.raises(TypeError):
        calculate_smaug_gold_victory_points(None,smaug_points=0,opponent_points=0)


def test_evidence_does_not_mutate_marker_state():
    state=recovered(3)
    before=state.markers
    calculate_smaug_gold_victory_points(state,smaug_points=19,opponent_points=4)
    assert state.markers==before

"""DEV-077-SMAUG-D5B — Gold Marker lifecycle contract tests."""
import pytest
from smaug_gold_markers import (
    GoldMarker, GoldMarkerLocation, SmaugGoldState, deploy_gold_markers,
    kill_gold_carrier, pick_up_gold_marker, pass_gold_marker,
)


def setup():
    return deploy_gold_markers(('A', 'B', 'C'), smaug_model_id='SMAUG:1:1')


def test_exactly_three_different_enemies_after_deployment():
    state=setup()
    assert len(state.markers)==3
    assert state.enemy_carrier_ids == {'A','B','C'}
    assert all(m.location is GoldMarkerLocation.CARRIED for m in state.markers)


@pytest.mark.parametrize('ids', [('A','A','C'),('A','B','SMAUG:1:1'),('A','B'),('', 'B','C')])
def test_invalid_deployment_rejected(ids):
    with pytest.raises(ValueError):
        deploy_gold_markers(tuple(ids), smaug_model_id='SMAUG:1:1')


def test_smaug_combat_kill_immediately_recovers_marker():
    state=kill_gold_carrier(setup(),marker_id='GOLD_1',slain_model_id='A',killed_by_smaug_in_combat=True)
    assert state.marker('GOLD_1').location is GoldMarkerLocation.RECOVERED
    assert state.recovered_count==1
    assert state.enemy_carrier_ids == {'B','C'}


def test_other_death_drops_gold():
    state=kill_gold_carrier(setup(),marker_id='GOLD_1',slain_model_id='A',killed_by_smaug_in_combat=False)
    assert state.marker('GOLD_1').location is GoldMarkerLocation.DROPPED
    assert state.marker('GOLD_1').carrier_id is None


def test_other_model_can_pick_up_dropped_marker():
    state=kill_gold_carrier(setup(),marker_id='GOLD_1',slain_model_id='A',killed_by_smaug_in_combat=False)
    state=pick_up_gold_marker(state,marker_id='GOLD_1',picking_model_id='D')
    assert state.marker('GOLD_1').carrier_id=='D'
    assert 'D' in state.enemy_carrier_ids


def test_smaug_pickup_recovers_and_removes_marker():
    state=kill_gold_carrier(setup(),marker_id='GOLD_1',slain_model_id='A',killed_by_smaug_in_combat=False)
    state=pick_up_gold_marker(state,marker_id='GOLD_1',picking_model_id='SMAUG:1:1')
    assert state.marker('GOLD_1').location is GoldMarkerLocation.RECOVERED
    assert state.recovered_count==1


def test_no_voluntary_pass():
    with pytest.raises(ValueError, match='never be passed'):
        pass_gold_marker(setup(),'GOLD_1','A','B')


def test_cannot_pickup_carried_marker():
    with pytest.raises(ValueError):
        pick_up_gold_marker(setup(),marker_id='GOLD_1',picking_model_id='D')


def test_cannot_pickup_recovered_marker():
    state=kill_gold_carrier(setup(),marker_id='GOLD_1',slain_model_id='A',killed_by_smaug_in_combat=True)
    with pytest.raises(ValueError):
        pick_up_gold_marker(state,marker_id='GOLD_1',picking_model_id='D')


def test_wrong_slain_carrier_rejected():
    with pytest.raises(ValueError):
        kill_gold_carrier(setup(),marker_id='GOLD_1',slain_model_id='B',killed_by_smaug_in_combat=True)


def test_previous_state_unchanged_by_transition():
    original=setup()
    new=kill_gold_carrier(original,marker_id='GOLD_1',slain_model_id='A',killed_by_smaug_in_combat=True)
    assert original.marker('GOLD_1').location is GoldMarkerLocation.CARRIED
    assert new != original


def test_unknown_marker_rejected():
    with pytest.raises(ValueError):
        setup().marker('GOLD_4')


def test_multiple_markers_can_be_recovered_independently():
    state=setup()
    for i,carrier in enumerate(('A','B','C'),1):
        state=kill_gold_carrier(state,marker_id=f'GOLD_{i}',slain_model_id=carrier,killed_by_smaug_in_combat=True)
    assert state.recovered_count==3
    assert state.enemy_carrier_ids==frozenset()

from army_resource_state import ArmyResourceState


def test_army_resource_state_stores_total_resources():
    state = ArmyResourceState(
        might=6,
        will=4,
        fate=3,
    )

    assert state.might == 6
    assert state.will == 4
    assert state.fate == 3
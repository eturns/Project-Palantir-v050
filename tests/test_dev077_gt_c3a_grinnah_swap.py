"""Focused 2024 Swap with Me! behaviour; explicit geometry inputs."""
import pytest
from types import SimpleNamespace
from grinnah_swap_with_me import GrinnahSwapContext, assess_grinnah_swap

def model(profile_id):
    return SimpleNamespace(profile=SimpleNamespace(id=profile_id))

def context(**overrides):
    data=dict(friendly_model_is_goblin=True,distance_inches=3,
              target_base_size_mm=25,start_of_fight_phase=True,
              before_heroic_actions=True)
    data.update(overrides)
    return GrinnahSwapContext(**data)

def test_legal_swap_and_no_movement():
    result=assess_grinnah_swap(model("GT_GRINNAH"),context())
    assert result.permitted and result.swaps_positions
    assert result.counts_as_moving is False

@pytest.mark.parametrize("changes",[
    {"friendly_model_is_goblin":False},
    {"distance_inches":3.01},
    {"target_base_size_mm":40},
    {"start_of_fight_phase":False},
    {"before_heroic_actions":False},
])
def test_ineligible_conditions(changes):
    assert not assess_grinnah_swap(model("GT_GRINNAH"),context(**changes)).permitted

def test_exact_range_limit():
    assert assess_grinnah_swap(model("GT_GRINNAH"),context(distance_inches=3)).permitted

def test_not_another_goblin():
    assert not assess_grinnah_swap(model("GT_KING"),context()).permitted

@pytest.mark.parametrize("changes",[
    {"distance_inches":-0.1},
    {"distance_inches":float("nan")},
    {"distance_inches":float("inf")},
    {"target_base_size_mm":0},
    {"target_base_size_mm":25.0},
    {"friendly_model_is_goblin":None},
])
def test_reject_bad_context(changes):
    with pytest.raises((ValueError,TypeError)):
        context(**changes)

def test_reject_wrong_context_type():
    with pytest.raises(TypeError):
        assess_grinnah_swap(model("GT_GRINNAH"),None)

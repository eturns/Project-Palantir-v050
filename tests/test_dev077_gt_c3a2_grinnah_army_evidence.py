"""DEV-077-GT-C3A2 fielded-model and context acceptance tests."""
from types import SimpleNamespace
import pytest
from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from grinnah_swap_army_evidence import GrinnahSwapArmyContext, assess_army_grinnah_swaps


@pytest.fixture(scope="module")
def profiles():
    return {p.id: ConfiguredProfile(p) for p in load_all_profiles()}


def army(*members):
    models = tuple(SimpleNamespace(id=id_, configured_profile=p) for id_, p in members)
    return SimpleNamespace(fielded_models=lambda: models)


def context(**changes):
    kwargs = dict(target_model_id="goblin-1", distance_inches=3,
                  start_of_fight_phase=True, before_heroic_actions=True)
    kwargs.update(changes)
    return GrinnahSwapArmyContext(**kwargs)


def roster(profiles):
    return army(("grinnah-1", profiles["GT_GRINNAH"]),
                ("goblin-1", profiles["GT_WARRIOR"]))


def test_valid_swap(profiles):
    (result,) = assess_army_grinnah_swaps(army=roster(profiles),
              contexts_by_grinnah_id={"grinnah-1": context()})
    assert result.eligible and result.target_model_id == "goblin-1"
    assert result.counts_as_moving is False


def test_unknown_context_not_false(profiles):
    (result,) = assess_army_grinnah_swaps(army=roster(profiles),contexts_by_grinnah_id={})
    assert not result.context_supplied and result.eligible is None


@pytest.mark.parametrize("changes", [
    {"distance_inches": 3.01}, {"start_of_fight_phase": False},
    {"before_heroic_actions": False},
])
def test_timing_and_distance(profiles, changes):
    (result,) = assess_army_grinnah_swaps(army=roster(profiles),
        contexts_by_grinnah_id={"grinnah-1": context(**changes)})
    assert result.eligible is False


def test_missing_target(profiles):
    with pytest.raises(ValueError, match="distinct fielded"):
        assess_army_grinnah_swaps(army=roster(profiles),
            contexts_by_grinnah_id={"grinnah-1": context(target_model_id="missing")})


def test_self_swap(profiles):
    with pytest.raises(ValueError, match="distinct fielded"):
        assess_army_grinnah_swaps(army=roster(profiles),
            contexts_by_grinnah_id={"grinnah-1": context(target_model_id="grinnah-1")})


def test_wrong_race(profiles):
    a = army(("grinnah-1",profiles["GT_GRINNAH"]),
             ("goblin-1",profiles["GT_GOLLUM"]))
    (result,) = assess_army_grinnah_swaps(army=a,
        contexts_by_grinnah_id={"grinnah-1":context()})
    assert result.eligible is False


def test_foreign_context(profiles):
    with pytest.raises(ValueError, match="non-Grinnah"):
        assess_army_grinnah_swaps(army=roster(profiles),
             contexts_by_grinnah_id={"goblin-1":context()})


def test_no_mutation(profiles):
    a=roster(profiles)
    before=a.fielded_models()
    assess_army_grinnah_swaps(army=a,contexts_by_grinnah_id={"grinnah-1":context()})
    assert a.fielded_models()==before


def test_no_grinnah(profiles):
    assert assess_army_grinnah_swaps(
        army=army(("goblin-1",profiles["GT_WARRIOR"])),contexts_by_grinnah_id={})==()


def test_invalid_mapping(profiles):
    with pytest.raises(TypeError):
        assess_army_grinnah_swaps(army=roster(profiles),contexts_by_grinnah_id=None)

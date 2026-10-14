import pytest

from hero_resource_state import HeroResourceState
from hero_hunting_resource_adapter import (
    HeroHuntingMethod, DeclaredMethodSpend, reconcile_cross_method_resources,
)


def spend(actor, method, **kwargs):
    return DeclaredMethodSpend(actor, method, **kwargs)


def state(might=1, will=2, fate=1):
    return HeroResourceState(might, will, fate)


def reconcile(spends, starts=None):
    return reconcile_cross_method_resources(
        starts if starts is not None else {"hero": state()}, tuple(spends)
    )


def test_melee_and_shooting_share_might():
    with pytest.raises(ValueError, match="Might exceeds"):
        reconcile([spend("hero",HeroHuntingMethod.MELEE,might=1),
                   spend("hero",HeroHuntingMethod.SHOOTING,might=1)])


def test_cast_and_resist_share_will():
    with pytest.raises(ValueError, match="Will exceeds"):
        reconcile([spend("hero",HeroHuntingMethod.MAGIC_CAST,will=2),
                   spend("hero",HeroHuntingMethod.MAGIC_RESIST,will=1)])


def test_defensive_fate_spends_share_pool():
    with pytest.raises(ValueError, match="Fate exceeds"):
        reconcile([spend("hero",HeroHuntingMethod.DEFENCE,fate=1),
                   spend("hero",HeroHuntingMethod.DEFENCE,fate=1)])


def test_mixed_spends_permitted_when_within_budget():
    result=reconcile([spend("hero",HeroHuntingMethod.SHOOTING,might=1),
                      spend("hero",HeroHuntingMethod.MAGIC_CAST,will=1),
                      spend("hero",HeroHuntingMethod.MAGIC_RESIST,will=1),
                      spend("hero",HeroHuntingMethod.DEFENCE,fate=1)])
    assert result.models[0].remaining == HeroResourceState(0,0,0)
    assert result.dashboard_score is None


def test_model_budgets_are_isolated():
    result=reconcile([spend("a",HeroHuntingMethod.MELEE,might=1),
                      spend("b",HeroHuntingMethod.SHOOTING,might=1)],
                     {"a": state(), "b": state()})
    assert all(m.remaining.remaining_might == 0 for m in result.models)


def test_unknown_actor_is_rejected():
    with pytest.raises(ValueError, match="unknown model"):
        reconcile([spend("other",HeroHuntingMethod.MELEE,might=1)])


def test_unspent_resources_unchanged():
    assert reconcile([]).models[0].remaining == state()


@pytest.mark.parametrize("method",list(HeroHuntingMethod))
def test_every_method_has_valid_domain(method):
    result=reconcile([spend("hero",method)])
    assert result.models[0].allocations[0].domain is not None


@pytest.mark.parametrize("field",["might","will","fate"])
def test_invalid_negative_spend(field):
    with pytest.raises(ValueError):
        spend("hero",HeroHuntingMethod.MELEE,**{field:-1})


def test_reject_implicit_boolean_spend():
    with pytest.raises(TypeError,match="integer"):
        spend("hero",HeroHuntingMethod.MELEE,might=True)


def test_reject_non_enum_method():
    with pytest.raises(TypeError,match="HeroHuntingMethod"):
        spend("hero","shooting",might=1)


def test_reject_non_declared_spend():
    with pytest.raises(TypeError,match="DeclaredMethodSpend"):
        reconcile(["unknown"])


def test_reject_nonexistent_model_state():
    with pytest.raises(TypeError,match="HeroResourceState"):
        reconcile([],{"hero":None})


def test_original_states_not_modified():
    initial=state()
    reconcile([spend("hero",HeroHuntingMethod.MAGIC_CAST,will=1)],{"hero":initial})
    assert initial.remaining_will == 2

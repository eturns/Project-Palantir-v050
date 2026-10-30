"""DEV-078-ROTN-C3: canonical army-wide Resistant to Magic grants."""
import pytest

from army_wide_magic_resistance import resolve_army_magic_resistance as resolve


def test_rise_grants_to_friendly_models():
    e = resolve(army_list_id="DG_ROTN", active_army_rule_ids=("DG_POWER_OF_THE_NECROMANCER",), model_is_friendly=True)
    assert e.granted and e.source_rule_id == "DG_POWER_OF_THE_NECROMANCER"


def test_rise_does_not_grant_to_enemy():
    e = resolve(army_list_id="DG_ROTN", active_army_rule_ids=("DG_POWER_OF_THE_NECROMANCER",), model_is_friendly=False)
    assert not e.granted and e.source_rule_id is None


def test_no_active_rule_means_no_grant():
    e = resolve(army_list_id="DG_ROTN", active_army_rule_ids=(), model_is_friendly=True)
    assert not e.granted


def test_other_necromancer_rule_is_insufficient():
    e = resolve(army_list_id="DG_ROTN", active_army_rule_ids=("DG_HIS_SPIRIT",), model_is_friendly=True)
    assert not e.granted


def test_pits_uses_same_resolver_when_rule_registered():
    e = resolve(army_list_id="DG_PITS", active_army_rule_ids=("DG_MAGICAL_VOID",), model_is_friendly=True)
    assert e.granted and e.source_rule_id == "DG_MAGICAL_VOID"


def test_pits_does_not_inherit_rise_rule():
    e = resolve(army_list_id="DG_PITS", active_army_rule_ids=("DG_POWER_OF_THE_NECROMANCER",), model_is_friendly=True)
    assert not e.granted


def test_unrelated_army_cannot_grant_with_matching_rule_id():
    e = resolve(army_list_id="AZOGS_HUNTERS", active_army_rule_ids=("DG_POWER_OF_THE_NECROMANCER",), model_is_friendly=True)
    assert not e.granted


def test_no_scores_or_resist_probability_invented():
    e = resolve(army_list_id="DG_ROTN", active_army_rule_ids=("DG_POWER_OF_THE_NECROMANCER",), model_is_friendly=True)
    assert e.dashboard_score is None and e.scenario_score is None
    assert not hasattr(e, "resist_probability")


@pytest.mark.parametrize("bad", ["", " ", None, 42])
def test_invalid_army_id_rejected(bad):
    with pytest.raises(ValueError):
        resolve(army_list_id=bad, active_army_rule_ids=(), model_is_friendly=True)


@pytest.mark.parametrize("bad", [None, 1, "yes"])
def test_friendliness_must_be_explicit_boolean(bad):
    with pytest.raises(TypeError):
        resolve(army_list_id="DG_ROTN", active_army_rule_ids=(), model_is_friendly=bad)


def test_invalid_rule_collection_rejected():
    with pytest.raises(TypeError):
        resolve(army_list_id="DG_ROTN", active_army_rule_ids="DG_POWER_OF_THE_NECROMANCER", model_is_friendly=True)


def test_invalid_rule_values_rejected():
    with pytest.raises(ValueError):
        resolve(army_list_id="DG_ROTN", active_army_rule_ids=("",), model_is_friendly=True)

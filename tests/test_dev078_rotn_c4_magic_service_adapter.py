"""DEV-078-ROTN-C4 opt-in service checks; no live scoring mutation."""
from types import SimpleNamespace

import pytest

from rotn_army_magic_service_adapter import (
    build_army_magic_resistance_inventory,
    analyse_imported_army_with_magic_resistance,
)


def lst(id, *rules):
    return SimpleNamespace(id=id, army_rules=[SimpleNamespace(id=r) for r in rules])


def army(monkeypatch, ids=("DG_NEC:1:1", "DG_WK:2:1")):
    # Lightweight test double keeps tests independent of list-builder fixtures.
    from army import Army
    a = object.__new__(Army)
    monkeypatch.setattr(Army, "fielded_models", lambda self: tuple(SimpleNamespace(id=i) for i in ids))
    return a


def test_rise_entitlement_follows_actual_fielded_ids(monkeypatch):
    a = army(monkeypatch)
    e = build_army_magic_resistance_inventory(a, lst("DG_ROTN", "DG_POWER_OF_THE_NECROMANCER"))
    assert e.eligible_model_ids == ("DG_NEC:1:1", "DG_WK:2:1")
    assert e.model_count == 2
    assert e.source_rule_id == "DG_POWER_OF_THE_NECROMANCER"
    assert e.dashboard_score is None and e.scenario_score is None


def test_other_rule_does_not_activate_grant(monkeypatch):
    e = build_army_magic_resistance_inventory(army(monkeypatch), lst("DG_ROTN", "DG_HIS_SPIRIT"))
    assert not e.eligible_model_ids and e.source_rule_id is None


def test_pits_can_reuse_same_grant_later(monkeypatch):
    e = build_army_magic_resistance_inventory(army(monkeypatch), lst("DG_PITS", "DG_MAGICAL_VOID"))
    assert e.source_rule_id == "DG_MAGICAL_VOID"


def test_unrelated_list_does_not_inherit_rule(monkeypatch):
    e = build_army_magic_resistance_inventory(army(monkeypatch), lst("GUNDABAD", "DG_POWER_OF_THE_NECROMANCER"))
    assert not e.eligible_model_ids


def test_duplicate_model_ids_rejected(monkeypatch):
    with pytest.raises(ValueError, match="distinct"):
        build_army_magic_resistance_inventory(army(monkeypatch, ("same", "same")), lst("DG_ROTN", "DG_POWER_OF_THE_NECROMANCER"))


def test_service_adds_separate_evidence_without_mutating_scores(monkeypatch):
    a = army(monkeypatch)
    scores = {"metric_assessments": {"magic": 0.42}, "battlefield_assessments": ("x",)}
    monkeypatch.setattr("rotn_army_magic_service_adapter.analyse_imported_army", lambda *args, **kwargs: scores)
    result = analyse_imported_army_with_magic_resistance(a, lst("DG_ROTN", "DG_POWER_OF_THE_NECROMANCER"), 700, object())
    assert result is not scores
    assert result["metric_assessments"] is scores["metric_assessments"]
    assert result["battlefield_assessments"] is scores["battlefield_assessments"]
    assert "mechanical_army_magic_resistance" not in scores
    assert len(result["mechanical_army_magic_resistance"].eligible_model_ids) == 2


def test_service_unrelated_army_returns_original_result(monkeypatch):
    a = army(monkeypatch)
    scores = {"metric_assessments": {"magic": 0.42}}
    monkeypatch.setattr("rotn_army_magic_service_adapter.analyse_imported_army", lambda *args, **kwargs: scores)
    assert analyse_imported_army_with_magic_resistance(a, lst("AZOGS_HUNTERS"), 700, object()) is scores


def test_unsupported_input_rejected():
    with pytest.raises(TypeError, match="Army"):
        build_army_magic_resistance_inventory(object(), lst("DG_ROTN"))

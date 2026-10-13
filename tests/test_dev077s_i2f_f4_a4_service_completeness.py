"""DEV-077S-I2-F closure: completeness is a gate, not a zero Magic score."""
from types import SimpleNamespace
import pytest
from army import Army
from loader import load_all_profiles
from relationship_loader import load_profile_spells
from rule_loader import load_spells
from services import army_analysis_service as service


def _isolate_legacy(monkeypatch):
    monkeypatch.setattr(service, "calculate_army_metric_densities", lambda *_: "densities")
    monkeypatch.setattr(service, "calculate_army_offensive_output_density", lambda *_: .2)
    monkeypatch.setattr(service, "build_shooting_benchmark_defender", lambda: object())
    monkeypatch.setattr(service, "calculate_army_shooting_output_density", lambda **_: .3)
    monkeypatch.setattr(service, "normalise_shooting_output_density", lambda _: .4)
    monkeypatch.setattr(service, "calculate_mechanical_defence_diagnostics", lambda *_: None)
    monkeypatch.setattr(service, "build_mobility_integration_contract", lambda *_: None)
    monkeypatch.setattr(service, "assess_army_metrics", lambda *_, **__: "unchanged_metrics")
    monkeypatch.setattr(service, "assess_battlefield", lambda *_: "unchanged_scenarios")


class AnalysisArmy(Army):
    def validate(self, limit):
        return ()
    def analysis_metrics(self):
        return "legacy"


def _army_with_necromancer(*, hydrated):
    profiles = {p.id: p for p in load_all_profiles()}
    if hydrated:
        load_profile_spells(profiles, load_spells())
    army = AnalysisArmy()
    army.add_profile(profiles["DG_NEC"])
    return army


def _analyse(army):
    return service.analyse_imported_army(army, object(), 700, object())


def test_missing_spells_show_incomplete_and_unavailable_magic(monkeypatch):
    _isolate_legacy(monkeypatch)
    result = _analyse(_army_with_necromancer(hydrated=False))
    assert result["mechanical_magic"] is None
    assert result["mechanical_magic_completeness"].status == "incomplete"
    assert len(result["mechanical_magic_completeness"].missing) == 9
    assert result["metric_assessments"] == "unchanged_metrics"
    assert result["battlefield_assessments"] == "unchanged_scenarios"


def test_hydrated_necromancer_shows_complete_magic(monkeypatch):
    _isolate_legacy(monkeypatch)
    result = _analyse(_army_with_necromancer(hydrated=True))
    assert result["mechanical_magic_completeness"].is_complete
    assert result["mechanical_magic"] is not None
    assert "COMPEL" in result["mechanical_magic"].distinct_spell_ids
    assert result["mechanical_magic"].dashboard_score is None
    assert result["battlefield_assessments"] == "unchanged_scenarios"


def test_empty_army_is_complete_zero_casters(monkeypatch):
    _isolate_legacy(monkeypatch)
    result = _analyse(AnalysisArmy())
    assert result["mechanical_magic_completeness"].is_complete
    assert result["mechanical_magic"].caster_count == 0


def test_legacy_double_has_no_false_complete_status(monkeypatch):
    _isolate_legacy(monkeypatch)
    fake = SimpleNamespace(validate=lambda _: (), analysis_metrics=lambda: "legacy")
    result = _analyse(fake)
    assert result["mechanical_magic_completeness"] is None
    assert result["mechanical_magic"] is None


def test_missing_catalogue_is_not_swallowed(monkeypatch):
    _isolate_legacy(monkeypatch)
    def corrupt(*_):
        raise FileNotFoundError("missing canonical spell catalogue")
    monkeypatch.setattr(service, "audit_army_magic_completeness", corrupt)
    with pytest.raises(FileNotFoundError, match="missing canonical"):
        _analyse(AnalysisArmy())

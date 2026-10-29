"""DEV-077-SMAUG-D6C — production adapter contracts and service wiring."""
import pytest
from army import Army
from smaug_scenario_service import build_smaug_scenario_service_evidence
from test_dev077_smaug_d5a_lust_for_gold_integration import make_army


def test_real_fielded_model_identity_and_uncertainty():
    army=make_army()
    evidence=build_smaug_scenario_service_evidence(army)
    assert evidence.smaug_model_id == army.fielded_models()[0].id
    assert evidence.dashboard_score is None
    assert evidence.scenario_score is None
    assert evidence.gold_victory_points is None


def test_no_smaug_yields_no_diagnostic():
    assert build_smaug_scenario_service_evidence(Army()) is None


def test_explicit_context_is_forwarded():
    army=make_army()
    evidence=build_smaug_scenario_service_evidence(
        army,scenario_context={"moving":False})
    assert evidence.lust_for_gold.charge_required is False


def test_unknown_context_rejected():
    with pytest.raises(ValueError,match="Unknown Smaug scenario inputs"):
        build_smaug_scenario_service_evidence(make_army(),scenario_context={"model_id":"fake"})


def test_foreign_army_rejects_context():
    with pytest.raises(ValueError,match="non-Smaug"):
        build_smaug_scenario_service_evidence(Army(),scenario_context={"moving":True})


def test_invalid_context_rejected():
    with pytest.raises(TypeError):
        build_smaug_scenario_service_evidence(make_army(),scenario_context=[1,2])


def test_invalid_army_rejected():
    with pytest.raises(TypeError):
        build_smaug_scenario_service_evidence(None)


def test_service_exposes_diagnostic_without_scenario_rescoring():
    import inspect
    from services.army_analysis_service import analyse_imported_army
    source=inspect.getsource(analyse_imported_army)
    assert "smaug_scenario_context=None" in source
    assert "build_smaug_scenario_service_evidence(" in source
    assert "result['mechanical_smaug_scenario'] = smaug_scenario" in source
    assert "smaug_scenario" not in source.split("metric_assessments = assess_army_metrics(",1)[1].split("battlefield_assessments =",1)[0]

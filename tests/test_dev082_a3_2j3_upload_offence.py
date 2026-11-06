"""DEV-082-A3-2J-3 per-upload and API additive contract acceptance.
Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).
"""
from copy import deepcopy
import json
from types import SimpleNamespace as S
import pytest

from web.backend.offence_upload_diagnostic_adapter import (
    build_uploaded_army_offence_api_evidence,
)
from web.backend.result_mapper import build_web_analysis_result
import provisional_offence_upload_evidence as collector


class DummyArmy:
    def __init__(self, count=4, fielded=2):
        self.count = count
        self.entries = [S(counts_as_model=True) for _ in range(fielded)]
    def model_count(self):
        return self.count


@pytest.fixture(autouse=True)
def use_dummy_army(monkeypatch):
    monkeypatch.setattr(collector, "Army", DummyArmy)


def view():
    return {
        "army_name": "Uploaded Sample", "total_points": 700,
        "model_count": 4, "metrics": {"offence": .55, "movement": .4},
        "scenarios": [{"id": i, "score": i/24} for i in range(24)],
        "provisional_capabilities": {"metrics": [{"metric_id": "offence", "rating": .55}]},
        "provisional_magic": {"display_only": True, "caster_count": 0},
    }


def failure():
    return collector._unqualified("unsupported_or_unverified_configuration", DummyArmy())


def test_invalid_army_never_calculated():
    assert collector.calculate_uploaded_army_offence_evidence(object())["reason_code"] == "invalid_army"


def test_empty_army_has_no_zero_score():
    result = collector.calculate_uploaded_army_offence_evidence(DummyArmy(count=0, fielded=0))
    assert result["status"] == "not_qualified"
    assert result["neutral_melee"] is None


def test_oversized_roster_fail_closed():
    out = collector.calculate_uploaded_army_offence_evidence(DummyArmy(count=301))
    assert out["reason_code"] == "analysis_limit_exceeded"


def test_too_many_entries_fail_closed():
    out = collector.calculate_uploaded_army_offence_evidence(DummyArmy(fielded=151))
    assert out["reason_code"] == "analysis_limit_exceeded"


def test_unsupported_configuration_does_not_break_base_analysis():
    assert collector.calculate_uploaded_army_offence_evidence(DummyArmy())["status"] == "not_qualified"


def test_failure_reason_not_leaking_internal_errors():
    out = collector.calculate_uploaded_army_offence_evidence(DummyArmy())
    assert "ModuleNotFoundError" not in str(out)
    assert "traceback" not in str(out).lower()


def test_unqualified_is_serialized_as_null_not_zero():
    out = build_uploaded_army_offence_api_evidence(failure())
    assert out["neutral_melee"] is None
    assert out["conditional_capabilities"] is None
    assert out["status"] == "not_qualified"
    assert out["safeguards"]["candidate_raw_density"] is None


def test_legacy_response_unchanged_when_field_absent():
    assert build_web_analysis_result(view())["analysis"] == view()


def test_unqualified_response_only_adds_field():
    before = build_web_analysis_result(view())
    x = {**view(), "provisional_offence": failure()}
    after = build_web_analysis_result(x)
    assert after["schema_version"] == "palantir-web-analysis-v1"
    assert {k: v for k,v in after["analysis"].items() if k != "provisional_offence"} == before["analysis"]


def test_24_scenarios_preserved():
    output=build_web_analysis_result({**view(), "provisional_offence": failure()})
    assert output["analysis"]["scenarios"] == view()["scenarios"]
    assert len(output["analysis"]["scenarios"]) == 24


def test_existing_metric_and_magic_preserved():
    output=build_web_analysis_result({**view(), "provisional_offence": failure()})["analysis"]
    assert output["metrics"] == view()["metrics"]
    assert output["provisional_magic"] == view()["provisional_magic"]
    assert output["provisional_capabilities"] == view()["provisional_capabilities"]


def test_json_safe():
    output=build_web_analysis_result({**view(), "provisional_offence": failure()})
    assert json.loads(json.dumps(output, allow_nan=False)) == output


def test_no_evidence_mutation():
    x=failure()
    before=deepcopy(x)
    build_uploaded_army_offence_api_evidence(x)
    assert x == before


@pytest.mark.parametrize("field, val", [
    ("candidate_raw_density", .4),
    ("production_scoring_changed", True),
    ("calibration_changed", True),
    ("promotion_authorised", True),
    ("scenario_score", .5),
    ("dashboard_score", .5),
    ("neutral_melee", {"value": .8}),
    ("conditional_capabilities", {"support": 10}),
    ("reason_code", "traceback"),
    ("stage", "unknown"),
])
def test_unsafe_unqualified_record_rejected(field, val):
    x=failure()
    x[field]=val
    with pytest.raises(ValueError):
        build_uploaded_army_offence_api_evidence(x)


def test_explicit_none_is_rejected():
    with pytest.raises(ValueError):
        build_web_analysis_result({**view(), "provisional_offence": None})


def test_missing_field_is_not_fabricated():
    assert "provisional_offence" not in build_web_analysis_result(view())["analysis"]


def test_fails_closed_when_model_count_invalid():
    x=failure()
    x["models"]=-1
    with pytest.raises(ValueError):
        build_uploaded_army_offence_api_evidence(x)


def test_failure_status_has_no_legacy_scoring_fields():
    serialized=build_uploaded_army_offence_api_evidence(failure())
    assert "legacy_reference" not in serialized
    assert serialized["safeguards"]["promotion_authorised"] is False


def test_source_indicates_no_deployment_or_weapon_selection():
    serialized=build_uploaded_army_offence_api_evidence(failure())
    assert serialized["neutral_melee"] is None
    assert "weapon_choice" not in str(serialized)


def test_qualified_collector_reuses_same_imported_army(monkeypatch):
    """Synthetic success path checks no reimport or cross-army substitution."""
    import sys
    import types
    army = DummyArmy(count=4, fielded=2)
    seen=[]
    script = {
        "offence_trapping_benchmark": ("build_trapping_qualified_offence_report", lambda a: (seen.append(a), "trap")[1]),
        "offence_weapon_qualification": ("build_weapon_qualified_offence_report", lambda a: (seen.append(a), "weapons")[1]),
        "offence_explicit_army_aggregation": ("make_fielded_offence_roster", lambda a: (seen.append(a), "roster")[1]),
        "offence_aggregation_methodology": ("classify_army_methodology", lambda k,t,r: {"key":k,"method":"m"}),
        "offence_multi_weapon_audit": ("audit_multi_weapon_report", lambda w, *, key: {"key":key,"multiple_weapon_models":0}),
        "offence_weapon_resolution_policy": ("qualify_multi_weapon_cohort", lambda c: {"status":"complete","armies_qualified":1,"rows":[{"key":"user_upload"}]}),
        "offence_neutral_baseline_completeness": ("qualify_neutral_baseline_completeness", lambda m,w: {"coverage":True}),
        "offence_neutral_mechanical_comparison": ("compare_neutral_mechanical_army", lambda c: {"numerical":True}),
        "offence_candidate_metric_qualification": ("qualify_neutral_metric_army", lambda n,c,m: {"qualified":True}),
        "offence_mechanical_attribution": ("replay_legacy_profile_states", lambda a: (seen.append(a), [1])[1]),
        "offence_presentation_contract": ("build_offence_presentation_row", lambda a,q,c: {"stage":"DEV-082-A3-2J-1","status":"qualified-synthetic"}),
        "army_offence_capability": ("calculate_army_offensive_output_density", lambda a, *, charge_probability: (seen.append(a),.6)[1]),
    }
    for mod, (func, impl) in script.items():
        module=types.ModuleType(mod)
        setattr(module,func,impl)
        monkeypatch.setitem(sys.modules,mod,module)
    # Attribution module has two functions.
    mod=sys.modules["offence_mechanical_attribution"]
    mod.attribute_army_neutral_difference=lambda q,r, *, production_check: {"attributed":True}
    result=collector.calculate_uploaded_army_offence_evidence(army)
    assert result["status"] == "qualified-synthetic"
    assert len(seen) == 5
    assert all(x is army for x in seen)

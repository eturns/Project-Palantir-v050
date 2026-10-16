"""Focused, dependency-free B8-B4 evidence-discovery contracts."""
from i2i_c3_b8b4_rule_implementation_evidence import build_report, matching_paths, tokens, read_inventory

def sample():
    return {"cross_army_verification_queue": [{
        "rule_id": "TERROR", "armies_affected": 2, "model_exposures": 13
    }, {
        "rule_id": "KNIFE_FIGHTER", "armies_affected": 1, "model_exposures": 31
    }]}

def test_variants():
    assert tokens("KNIFE_FIGHTER") == ("KNIFE_FIGHTER", "KNIFE FIGHTER")

def test_exact_matching():
    files = {"a.py": "TERROR = True", "b.py": "ANTI_TERROR_TEST"}
    assert matching_paths("TERROR", files) == ["a.py"]

def test_no_evidence_not_marked_missing():
    report = build_report(sample(), source={}, tests={})
    row = report["rules"][0]
    assert row["evidence_discovery"] == "no_explicit_references_found"
    assert row["runtime_mechanical_verification"] == "not_verified"

def test_candidates_not_approved():
    report = build_report(sample(), source={"src/a.py": "TERROR"},
                          tests={"tests/test_a.py": "TERROR"})
    row = report["rules"][0]
    assert row["evidence_discovery"] == "source_and_tests_found"
    assert row["calibration_approved"] is False
    assert report["full_special_rules_approved"] is False

def test_reports_all_queue_rows():
    assert build_report(sample(), source={}, tests={})["rules_scanned"] == 2

def test_flags_are_read_only():
    report = build_report(sample(), source={}, tests={})
    assert report["production_scoring_modified"] is False
    assert report["calibration_anchors_approved"] is False


def test_utf16_powershell_report(tmp_path):
    import json
    path = tmp_path / "report.json"
    original = sample()
    path.write_bytes(json.dumps(original).encode("utf-16"))
    assert read_inventory(path) == original


def test_utf8_bom_report(tmp_path):
    import json
    path = tmp_path / "report.json"
    original = sample()
    path.write_bytes(json.dumps(original).encode("utf-8-sig"))
    assert read_inventory(path) == original


def test_utf8_report(tmp_path):
    import json
    path = tmp_path / "report.json"
    original = sample()
    path.write_bytes(json.dumps(original).encode("utf-8"))
    assert read_inventory(path) == original

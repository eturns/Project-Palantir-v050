"""Focused unit tests for read-only source inspection."""
import importlib.util
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "i2i_mirkwood_profile_mechanics_audit.py"
spec = importlib.util.spec_from_file_location("mirkwood_audit", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def test_profile_only_scope():
    assert module.audit()["army_special_rules_included"] is False

def test_no_scoring_changes():
    assert module.audit()["production_scoring_modified"] is False

def test_expected_rules_present():
    assert len(module.audit()["rules"]) == 9

def test_implementation_present_only_with_marker(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "sharpshooter.py").write_text("SHARPSHOOTER_RULE_ID = 'SHARPSHOOTER'")
    result = module.audit(tmp_path)
    assert result["rules"]["SHARPSHOOTER"]["status"] == "source_implementation_evidence_found"
    assert result["rules"]["DEADLY_SHOT"]["status"] == "not_verified_by_targeted_source_audit"

def test_rule_absence_not_claimed_as_definite():
    result = module.audit(Path("/not-a-project"))
    assert all(v["status"] == "not_verified_by_targeted_source_audit" for v in result["rules"].values())

def test_end_to_end_never_claimed():
    assert not any(v["runtime_end_to_end_verified"] for v in module.audit()["rules"].values())

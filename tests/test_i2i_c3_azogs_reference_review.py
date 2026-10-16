"""Focused tests for D7-B3 review without inventing actual measured values."""
import hashlib
import json
from pathlib import Path

import pytest
from i2i_c3_azogs_reference_review import review, run


@pytest.fixture
def inputs():
    roster = json.loads((Path(__file__).parent / "azogs-hunters.json").read_text(encoding="utf-8")) if (Path(__file__).parent / "azogs-hunters.json").exists() else {
        "edition":"v2024", "armyList":"Azog's Hunters", "warbands":[
            {"hero":{"options":[{"id":"OPT0690"}]}, "meta":{"points":318}, "units":[{"model_id":"[azog's-hunters] hunter-orc-warg-rider","quantity":6}]},
            {"hero":{"options":[{"id":"OPT0691"}]}, "meta":{"points":256}, "units":[{"model_id":"[azog's-hunters] fell-warg","quantity":7}]},
            {"hero":{"options":[]}, "meta":{"points":123}, "units":[{"model_id":"[azog's-hunters] hunter-orc-warrior","quantity":8}]},
        ]}
    evidence={"source":"fresh_real_army_engine_run","army_key":"azogs_hunters_700", "roster_sha256":"a"*64,"points":697,"models":24,"analysis_commit":"b2d1132","measurements":[{} for _ in range(10)],"reference_anchors_approved":False,"production_scoring_enabled":False,"scenario_scoring_changed":False}
    return roster, evidence


def evaluate(inputs):
    r,e=inputs
    return review(r,e,roster_sha256="a"*64)


def test_valid_identity_classification(inputs):
    result=evaluate(inputs)
    assert result["evidence_identity_and_composition_verified"] is True
    assert result["warg_riders"]==6 and result["fell_wargs"]==7
    assert result["mount_option_heroes"]==2
    assert result["reference_archetype"]=="mobile_mixed_assault"


def test_not_calibration_approved(inputs):
    r=evaluate(inputs)
    assert not r["army_list_rules_legality_verified"]
    assert not r["calibration_eligible"] and not r["anchors_approved"]


@pytest.mark.parametrize("field,value,blocker", [
    ("points",694,"reference_points_mismatch"),
    ("models",23,"model_count_mismatch"),
    ("roster_sha256","b"*64,"roster_content_hash_mismatch"),
    ("army_key","other","wrong_evidence_army_key"),
    ("source","old_data","not_a_fresh_engine_run"),
    ("production_scoring_enabled",True,"scoring_isolation_not_confirmed"),
])
def test_evidence_tamper_blocked(inputs,field,value,blocker):
    inputs[1][field]=value
    assert blocker in evaluate(inputs)["blockers"]


def test_missing_mounts_blocks_archetype(inputs):
    for wb in inputs[0]["warbands"]:
        wb["hero"]["options"]=[]
    assert "insufficient_roster_evidence_for_mobile_archetype" in evaluate(inputs)["blockers"]


def test_wrong_faction_blocked(inputs):
    inputs[0]["armyList"]="Other"
    assert "wrong_edition_or_army_list" in evaluate(inputs)["blockers"]


def test_no_overwrite(tmp_path,inputs):
    roster,evidence=inputs
    rp,ep,op=(tmp_path/f for f in ("roster.json","evidence.json","out.json"))
    rp.write_text(json.dumps(roster));ep.write_text(json.dumps(evidence));op.write_text("existing")
    with pytest.raises(ValueError,match="overwrite"):
        run(rp,ep,op)


def test_run_uses_actual_hash(tmp_path,inputs):
    roster,evidence=inputs
    rp,ep,op=(tmp_path/f for f in ("roster.json","evidence.json","out.json"))
    rp.write_text(json.dumps(roster))
    evidence["roster_sha256"]=hashlib.sha256(rp.read_bytes()).hexdigest()
    ep.write_text(json.dumps(evidence))
    result=run(rp,ep,op)
    assert result["evidence_identity_and_composition_verified"]
    assert json.loads(op.read_text())["export_points"]==697

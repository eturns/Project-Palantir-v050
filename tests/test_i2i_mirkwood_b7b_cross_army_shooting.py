"""B7-B: explicit reference data, no synthetic baseline or silent omissions."""
import pytest
from i2i_mirkwood_b7b_cross_army_shooting import compare, evaluate_army

def test_missing_armies_reported_not_silently_omitted(tmp_path):
    result=compare({"missing":str(tmp_path/"nonexistent.json")})
    assert result["armies"]==[]
    assert result["blockers"][0]["status"]=="missing_fixture"
    assert result["comparison_available"] is False

def test_empty_input_no_comparison():
    assert compare({})["comparison_available"] is False

def test_no_approved_calibration():
    result=compare({})
    assert result["calibration_anchors_approved"] is False
    assert result["production_scoring_modified"] is False

@pytest.fixture(scope="module")
def mirkwood_result():
    result=compare({"mirkwood":"tests/fixtures/rangers-of-mirkwood.json"})
    assert not result["blockers"],result["blockers"]
    return result

def test_mirkwood_is_700_points(mirkwood_result):
    army=mirkwood_result["armies"][0]
    assert army["points"]==700 and army["models"]==33
    assert army["reference_points_eligible"] is True

def test_mirkwood_has_33_shooters(mirkwood_result):
    assert mirkwood_result["armies"][0]["armed_shooters"]==33

def test_mirkwood_has_six_benchmark_rows(mirkwood_result):
    assert len(mirkwood_result["armies"][0]["benchmarks"])==6

@pytest.mark.parametrize("defence", (3,5,7))
def test_mirkwood_attack_count(mirkwood_result, defence):
    assert all(r["normal_attacks"]==36 for r in mirkwood_result["armies"][0]["benchmarks"] if r["defence"]==defence)

def test_no_single_army_ranking(mirkwood_result):
    assert mirkwood_result["comparison_available"] is False

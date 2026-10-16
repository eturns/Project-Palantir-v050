"""B6: shooting benchmark integrity and numeric invariants."""
import pytest
from i2i_mirkwood_b6_shooting_benchmarks import measure, benchmark_defender

@pytest.fixture(scope="module")
def report():
    return measure()

def test_six_scenarios(report):
    assert len(report["benchmarks"]) == 6

def test_all_defence_benchmarks(report):
    assert {(v["defence"],v["moved"]) for v in report["benchmarks"]} == {
        (d,m) for d in (3,5,7) for m in (False,True)
    }

@pytest.mark.parametrize("defence", (3,5,7))
def test_stationary_and_moving_report_eligible_models_and_attacks(report,defence):
    rows=[r for r in report["benchmarks"] if r["defence"]==defence]
    assert len(rows)==2
    assert all(r["eligible_models"]==33 and r["normal_attacks"]==36 for r in rows)

@pytest.mark.parametrize("moved", (False,True))
def test_wounds_decrease_as_defence_rises(report,moved):
    rows=sorted((r for r in report["benchmarks"] if r["moved"]==moved),
                key=lambda r:r["defence"])
    assert rows[0]["expected_wounds"] > rows[1]["expected_wounds"] > rows[2]["expected_wounds"] > 0

@pytest.mark.parametrize("defence", (3,5,7))
def test_movement_does_not_improve_output(report,defence):
    stationary=next(r for r in report["benchmarks"] if r["defence"]==defence and not r["moved"])
    moved=next(r for r in report["benchmarks"] if r["defence"]==defence and r["moved"])
    assert moved["expected_wounds"] <= stationary["expected_wounds"]

@pytest.mark.parametrize("defence", (3,5,7))
def test_density_matches_wounds_per_100_points(report,defence):
    r=next(r for r in report["benchmarks"] if r["defence"]==defence and not r["moved"])
    assert r["expected_wounds_per_100_points"] == pytest.approx(r["expected_wounds"]/7)

def test_all_four_profile_types_present(report):
    expected={"MW_LEGOLAS","MW_TAURIEL","MW_RANGER_CAPTAIN","MW_RANGER"}
    assert all(set(row["by_profile"])==expected for row in report["benchmarks"])

def test_no_calibration_or_production_scores(report):
    assert report["calibration_anchors_approved"] is False
    assert report["production_scoring_modified"] is False

def test_defender_characteristics():
    assert benchmark_defender(5).effective_defence == 5

def test_invalid_defence_rejected():
    with pytest.raises(ValueError):
        benchmark_defender(10)

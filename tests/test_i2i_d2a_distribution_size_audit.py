"""D2-A descriptive analysis checks, no production imports."""
from copy import deepcopy
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i2i_d2a_distribution_size_audit import analyse, read_json, pearson, ROOT, METRICS

@pytest.fixture(scope='module')
def report():
    return analyse(read_json(ROOT/'i2i_d1_measurement_matrix.json'),
                   read_json(ROOT/'b8a_cohort_intake.json'))

def test_six_armies_and_five_metrics(report):
    assert report['armies']==6
    assert tuple(report['metrics'])==METRICS

def test_expected_ranking(report):
    assert report['distributions']['shooting']['descending_rank'][0]['army']=='rangers_of_mirkwood'
    assert report['distributions']['mobility']['descending_rank'][0]['army']=='azogs_hunters'

def test_defence_decomposition(report):
    for row in report['defence_size_decomposition']:
        assert row['implied_total_survival_contribution']==pytest.approx(
            row['implied_mean_survival_contribution_per_model']*row['models'])

def test_not_approving_calibration(report):
    assert report['calibration_thresholds_fitted'] is False
    assert report['calibration_anchors_approved'] is False
    assert report['production_scoring_modified'] is False

def test_pearson_constant_is_unavailable():
    assert pearson([1,1,1],[2,3,4]) is None

def test_wrong_matrix_status_blocks():
    with pytest.raises(ValueError):
        analyse({'stage':'I2-I-D1','status':'incomplete'}, {'stage':'B8-A','intake_passed':6})

def test_missing_measurement_blocks():
    d=read_json(ROOT/'i2i_d1_measurement_matrix.json')
    d=deepcopy(d)
    d['rows'][0]['measurements']['defence']=None
    with pytest.raises(ValueError):
        analyse(d,read_json(ROOT/'b8a_cohort_intake.json'))

def test_non_matching_intake_blocks():
    d=read_json(ROOT/'i2i_d1_measurement_matrix.json')
    b=deepcopy(read_json(ROOT/'b8a_cohort_intake.json'))
    b['results'][0]['key']='other'
    with pytest.raises(ValueError):
        analyse(d,b)

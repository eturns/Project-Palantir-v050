"""C1 tests: no live rosters claimed, only structural extraction fixtures."""
from types import SimpleNamespace
import pytest

from unified_capability_inventory import METRIC_NAMES
from unified_calibration_contract import EvidenceAvailability
from unified_real_army_measurements import extract_mechanical_army_snapshot


def make_analysis():
    return {
        'metric_assessments': [
            SimpleNamespace(metric='offence', value=0.69, rating='Very Weak'),
            SimpleNamespace(metric='shooting', value=0.0, rating='Very Weak'),
        ],
        'mechanical_defence': {
            'combat_density': 1.25, 'combat_survival': .7,
            'recovery_density': 1.4, 'engagements': 3,
        },
    }


def extract(**kwargs):
    return extract_mechanical_army_snapshot(
        army_key='fixture_army', fixture_id='synthetic_fixture',
        analysis=make_analysis(), **kwargs,
    )


def test_all_ten_in_canonical_order():
    assert tuple(x.metric for x in extract().measurements) == METRIC_NAMES


def test_offence_raw_density_not_rating():
    assert extract().measurements[0].value == .69
    assert 'per 100' in extract().measurements[0].unit


def test_defence_uses_combat_not_recovery_density():
    assert extract().measurements[1].value == 1.25
    assert 'engagements=3' in extract().measurements[1].population


def test_shooting_dashboard_zero_not_mistaken_for_raw_zero():
    shooting = extract().measurements[4]
    assert shooting.value is None
    assert shooting.availability is EvidenceAvailability.UNAVAILABLE


def test_explicit_raw_shooting_zero_is_valid():
    assert extract(raw_shooting_output_density=0).measurements[4].value == 0


def test_raw_shooting_positive_is_valid():
    assert extract(raw_shooting_output_density=.12).measurements[4].value == .12


def test_no_production_scoring():
    assert extract().production_scoring_enabled is False


def test_missing_metrics_not_zero():
    assert all(x.value is None for x in extract().measurements[2:4])


def test_hero_hunting_unavailable():
    assert extract().measurements[-1].availability is EvidenceAvailability.UNAVAILABLE


def test_counts_without_raw_shooting():
    r = extract()
    assert r.available_count == 2 and len(r.unresolved_metrics) == 8


def test_counts_with_raw_shooting():
    r = extract(raw_shooting_output_density=.1)
    assert r.available_count == 3 and len(r.unresolved_metrics) == 7


@pytest.mark.parametrize('key', ['army_key', 'fixture_id', 'source_commit'])
def test_invalid_identity(key):
    args = {'army_key':'x','fixture_id':'y','source_commit':'z', 'analysis':make_analysis()}
    args[key] = ''
    with pytest.raises(ValueError):
        extract_mechanical_army_snapshot(**args)


@pytest.mark.parametrize('value', [float('nan'), float('inf'), True, '0.2'])
def test_reject_invalid_raw_shooting(value):
    with pytest.raises(ValueError):
        extract(raw_shooting_output_density=value)


def test_reject_wrong_analysis_type():
    with pytest.raises(TypeError):
        extract_mechanical_army_snapshot(army_key='a', fixture_id='b', analysis=[])


def test_reject_duplicate_assessment():
    a = make_analysis()
    a['metric_assessments'].append(SimpleNamespace(metric='offence', value=1, rating='Strong'))
    with pytest.raises(ValueError):
        extract_mechanical_army_snapshot(army_key='a', fixture_id='b', analysis=a)


def test_defence_requires_engagement_count():
    a = make_analysis()
    del a['mechanical_defence']['engagements']
    result = extract_mechanical_army_snapshot(army_key='a', fixture_id='b', analysis=a)
    assert result.measurements[1].value is None


def test_missing_analysis_fields_are_unavailable():
    r = extract_mechanical_army_snapshot(army_key='a', fixture_id='b', analysis={})
    assert r.available_count == 0


def test_source_commit_preserved():
    assert extract().source_commit == 'b2d1132'

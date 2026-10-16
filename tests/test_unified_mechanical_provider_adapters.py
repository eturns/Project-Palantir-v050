"""C2: structural interface tests, not measured real-army or calibration tests."""
from types import SimpleNamespace as S
import pytest

from unified_calibration_contract import EvidenceAvailability as E
from unified_mechanical_provider_adapters import (
    ProviderEvidenceBundle, extract_provider_measurement, extend_mechanical_army_snapshot,
)
from unified_real_army_measurements import extract_mechanical_army_snapshot
from unified_capability_inventory import METRIC_NAMES


def mobility(v=5.5, metric_id='mobility.open_ground.mean', unit='movement_accessibility_index'):
    return S(open_ground=S(value=v, metric_id=metric_id, unit=unit, assumptions=('open terrain',)))


def courage(v=.75, metric_id='courage.friendly.pass_probability', unit='probability'):
    return S(friendly_reliability=S(value=v, metric_id=metric_id, unit=unit, assumptions=('standard test',)))


def magic(v=.6, count=2):
    return S(one_will_probability_weighted_mean=v, caster_count=count, assumptions=('single attempt',))


def base():
    return extract_mechanical_army_snapshot(army_key='synthetic', fixture_id='fixture', analysis={})


@pytest.mark.parametrize('metric', ('control', 'command', 'objective', 'hero_hunting'))
def test_conditional_providers_do_not_invent_scalar(metric):
    result = extract_provider_measurement(metric, S(dashboard_score=1.0))
    assert result.value is None and result.availability is E.UNAVAILABLE
    assert result.unresolved

@pytest.mark.parametrize('metric', ('mobility', 'courage', 'magic'))
def test_missing_provider_not_zero(metric):
    r = extract_provider_measurement(metric, None)
    assert r.value is None and r.availability is E.UNAVAILABLE


def test_mobility_raw_index():
    r = extract_provider_measurement('mobility', mobility())
    assert r.value == 5.5 and r.availability is E.AVAILABLE
    assert r.unit == 'movement_accessibility_index'


def test_courage_raw_probability():
    r = extract_provider_measurement('courage', courage())
    assert r.value == .75 and r.availability is E.AVAILABLE


def test_magic_is_partial_even_when_numeric():
    r = extract_provider_measurement('magic', magic())
    assert r.value == .6 and r.availability is E.PARTIAL and r.unresolved

@pytest.mark.parametrize('v', (float('nan'), float('inf'), True, '6'))
def test_mobility_invalid_numeric_not_available(v):
    assert extract_provider_measurement('mobility', mobility(v)).availability is E.UNAVAILABLE


def test_wrong_mobility_unit_rejected():
    assert extract_provider_measurement('mobility', mobility(unit='inches')).value is None


def test_wrong_courage_metric_id_rejected():
    assert extract_provider_measurement('courage', courage(metric_id='other')).value is None

@pytest.mark.parametrize('v,count', ((None,1),(.5,0),(.5,True),(1.2,1),(-.1,1)))
def test_magic_incomplete_or_invalid(v,count):
    assert extract_provider_measurement('magic', magic(v,count)).availability is E.UNAVAILABLE


def test_snapshot_retains_canonical_order_and_identity():
    a=base()
    b=extend_mechanical_army_snapshot(a, ProviderEvidenceBundle(mobility=mobility(), courage=courage(), magic=magic()))
    assert tuple(m.metric for m in b.measurements)==METRIC_NAMES
    assert (a.army_key,a.fixture_id,a.source_commit)==(b.army_key,b.fixture_id,b.source_commit)
    assert b.available_count==2
    assert 'magic' in b.unresolved_metrics
    assert not b.production_scoring_enabled


def test_c1_values_never_overwritten():
    from types import SimpleNamespace
    a=extract_mechanical_army_snapshot(army_key='a', fixture_id='b',
        analysis={'metric_assessments':[SimpleNamespace(metric='offence',value=.4)],
                  'mechanical_defence':{'combat_density':1.0,'engagements':3}},
        raw_shooting_output_density=.3)
    b=extend_mechanical_army_snapshot(a, ProviderEvidenceBundle(mobility=mobility()))
    assert b.measurements[:2] == a.measurements[:2]
    assert b.measurements[4] == a.measurements[4]


def test_complete_snapshot_is_immutable():
    a=base()
    extend_mechanical_army_snapshot(a, ProviderEvidenceBundle(mobility=mobility()))
    assert a.measurements[2].value is None


def test_invalid_input_type_rejected():
    with pytest.raises(TypeError): extend_mechanical_army_snapshot('not a snapshot',ProviderEvidenceBundle())
    with pytest.raises(TypeError): extend_mechanical_army_snapshot(base(), {})
    with pytest.raises(KeyError): extract_provider_measurement('defence', None)

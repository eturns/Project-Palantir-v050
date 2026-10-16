"""P2-C1: provisional highs/lows must not leak legacy metric assessments."""
import pytest
from desktop_app import build_strengths_summary, build_weaknesses_summary


def vm(rows, *, panel=True):
    output = {
        'strengths': ({'metric': 'Magic', 'rating': 'Exceptional', 'value': 0.95},),
        'weaknesses': ({'metric': 'Shooting', 'rating': 'Very Weak', 'value': 0.97},),
    }
    if panel:
        output['provisional_capabilities'] = {
            'display_only': True, 'production_scoring_changed': False,
            'defence_independent_composite_weighting_allowed': False,
            'metrics': tuple(rows),
        }
    return output


def item(label, rating, status='evaluated'):
    return {'label': label, 'rating': rating, 'status': status}


def test_legacy_values_not_exposed_when_provisional_active():
    v = vm([item('Army Survival Density', .766), item('Per-Model Resilience', .263)])
    good = build_strengths_summary(v)
    low = build_weaknesses_summary(v)
    assert 'Army Survival Density: 0.766' in good
    assert 'Magic' not in good
    assert 'Shooting' not in low
    assert 'None evaluated' in low


def test_missing_is_not_zero_and_not_a_weakness():
    v = vm([item('Offence', None, 'not_evaluated'), item('Courage', None, 'conditional')])
    assert 'Offence' not in build_weaknesses_summary(v)
    assert 'Courage' not in build_weaknesses_summary(v)


def test_measured_zero_is_a_valid_low_reading():
    assert 'Stationary Shooting: 0.000' in build_weaknesses_summary(vm([item('Stationary Shooting', 0.0)]))


def test_provisional_comparison_does_not_claim_universal_quality():
    text = build_strengths_summary(vm([item('Mobility', 1.0)]))
    assert 'frozen cohort' in text
    assert 'not scenario scoring' in text


def test_legacy_fallback_still_works_for_non_provisional_callers():
    assert 'Magic: Exceptional' in build_strengths_summary(vm([], panel=False))
    assert 'Shooting: Very Weak' in build_weaknesses_summary(vm([], panel=False))


@pytest.mark.parametrize('key,value', [('display_only', False), ('production_scoring_changed', True), ('defence_independent_composite_weighting_allowed', True)])
def test_invalid_panel_safeguards_fail_closed(key,value):
    v = vm([item('Defence', 0.9)])
    v['provisional_capabilities'][key] = value
    with pytest.raises(ValueError):
        build_strengths_summary(v)


def test_invalid_rating_fails_closed():
    with pytest.raises(ValueError):
        build_weaknesses_summary(vm([item('Broken', 1.1)]))

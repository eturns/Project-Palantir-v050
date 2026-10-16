"""Non-mutating Mirkwood prerequisite audit tests."""
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from i2i_c3_mirkwood_gap_audit import analyze_export, REQUIRED_MODELS


def roster():
    return {
        'armyList': 'Rangers of Mirkwood',
        'warbands': [
            {'hero': {'model_id': '[rangers-of-mirkwood] legolas-greenleaf-prince-of-mirkwood', 'options': [{'id': 'OPT0771'}]},
             'units': [{'model_id': '[rangers-of-mirkwood] mirkwood-ranger', 'quantity': 10}],
             'meta': {'bows': 0}},
            {'hero': {'model_id': '[rangers-of-mirkwood] tauriel-ranger-of-mirkwood', 'options': [{'id': 'OPT0772'}]},
             'units': [{'model_id': '[rangers-of-mirkwood] mirkwood-ranger', 'quantity': 10}],
             'meta': {'bows': 0}},
            {'hero': {'model_id': '[rangers-of-mirkwood] mirkwood-ranger-captain', 'options': []},
             'units': [{'model_id': '[rangers-of-mirkwood] mirkwood-ranger', 'quantity': 10}],
             'meta': {'bows': 0}},
        ],
    }


def test_exact_four_models():
    assert set(analyze_export(roster())[0]) == set(REQUIRED_MODELS)


def test_thirty_rangers():
    assert analyze_export(roster())[0]['[rangers-of-mirkwood] mirkwood-ranger'] == 30


def test_three_heroes():
    assert sum(analyze_export(roster())[0].values()) == 33


def test_bow_limit_zero_not_shooters():
    assert analyze_export(roster())[2] == 0
    assert analyze_export(roster())[0]['[rangers-of-mirkwood] mirkwood-ranger'] > 0


def test_selected_options_preserved():
    assert analyze_export(roster())[1] == {'OPT0771', 'OPT0772'}


def test_unknown_army_rejected():
    r = roster(); r['armyList'] = 'Unknown'
    with pytest.raises(ValueError): analyze_export(r)


@pytest.mark.parametrize('n', [-1, 0, 1.5, True])
def test_invalid_quantities_rejected(n):
    r = roster(); r['warbands'][0]['units'][0]['quantity'] = n
    with pytest.raises(ValueError): analyze_export(r)


def test_empty_roster():
    assert analyze_export({'armyList': 'Rangers of Mirkwood', 'warbands': []}) == ({}, set(), 0)

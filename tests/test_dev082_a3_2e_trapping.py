"""A3-2E trapping benchmark acceptance; injected canonical evaluator."""
from types import SimpleNamespace as NS
import pytest

from offence_trapping_benchmark import compare_trapping_states, build_trapping_qualified_offence_report


def cfg(*ids):
    return NS(profile=NS(id='P'), effective_wargear=tuple(NS(id=v) for v in ids))


def outcome(p, weighted=None):
    return NS(uncharged=p, charged_without_cavalry_bonus=p,
              charged_with_cavalry_bonus=p, weighted=weighted)


def evaluator(profile, weapon_id, trapped):
    return outcome(0.75 if trapped else 0.5)


def test_trapped_gain():
    r = compare_trapping_states(cfg('WG_FANGS'), 'WG_FANGS', evaluator=evaluator)
    assert [x['absolute_improvement'] for x in r['conditional_combat_states']] == [0.25] * 3


def test_two_states_passed_explicitly():
    observed = []
    def collect(a, w, trapped):
        observed.append(trapped)
        return outcome(0.7 if trapped else 0.3)
    compare_trapping_states(cfg('WG_FANGS'), 'WG_FANGS', evaluator=collect)
    assert observed == [False, True]


def test_no_trapping_frequency_inferred():
    r = compare_trapping_states(cfg('WG_FANGS'), 'WG_FANGS', evaluator=evaluator)
    assert r['trapping_frequency'] is None and not r['trapping_frequency_inferred']


def test_no_weapon_choice_inferred():
    assert compare_trapping_states(cfg('WG_FANGS'), 'WG_FANGS', evaluator=evaluator)['selected_weapon_inferred'] is False


def test_doubled_strikes_do_not_guarantee_kill():
    assert compare_trapping_states(cfg('WG_FANGS'), 'WG_FANGS', evaluator=evaluator)['conditional_combat_states'][0]['trapped_probability'] < 1


def test_unowned_weapon_rejected():
    with pytest.raises(ValueError, match='not equipped'):
        compare_trapping_states(cfg('WG_FANGS'), 'WG_SPEAR', evaluator=evaluator)


def test_missing_weapon_id_rejected():
    with pytest.raises(ValueError):
        compare_trapping_states(cfg('WG_FANGS'), '', evaluator=evaluator)


@pytest.mark.parametrize('bad', [None, float('nan'), float('inf'), -0.1, 1.1])
def test_invalid_probability_fails_closed(bad):
    with pytest.raises(ValueError, match='probability'):
        compare_trapping_states(cfg('WG_FANGS'), 'WG_FANGS', evaluator=lambda a,w,t: outcome(bad))


def test_trapping_cannot_reduce_probability():
    with pytest.raises(ValueError, match='reduced'):
        compare_trapping_states(cfg('WG_FANGS'), 'WG_FANGS', evaluator=lambda a,w,t: outcome(0.2 if t else 0.6))


def test_unverified_charge_mixture_rejected():
    with pytest.raises(ValueError, match='charge frequency'):
        compare_trapping_states(cfg('WG_FANGS'), 'WG_FANGS', evaluator=lambda a,w,t: outcome(0.5, weighted=0.5))


def army():
    return NS(entries=(NS(counts_as_model=True, configured_profile=cfg('WG_FANGS'), quantity=2),
                       NS(counts_as_model=True, configured_profile=cfg('WG_HAND_WEAPON','WG_SPEAR'), quantity=1)))


def base():
    return {'stage':'DEV-082-A3-2D','candidate_raw_density':None,'comparable':False,
            'profile_rows': [
                {'profile_id':'P','quantity':2,'weapon_options':{'status':'single_recognised_option','candidate_weapon_ids':['WG_FANGS'],'unclassified_wargear_ids':[]}},
                {'profile_id':'P','quantity':1,'weapon_options':{'status':'multiple_options','candidate_weapon_ids':['WG_HAND_WEAPON','WG_SPEAR'],'unclassified_wargear_ids':[]}},
            ]}


def report(source=None):
    return build_trapping_qualified_offence_report(army(), report_builder=lambda a:base() if source is None else source, evaluator=evaluator)


def test_report_computes_single_option_only():
    x=report()
    assert x['profile_rows'][0]['trapping_benchmark'] is not None
    assert x['profile_rows'][1]['trapping_benchmark'] is None
    assert x['trapping_benchmark_model_status_counts']=={'paired_conditional_outcomes':2,'weapon_unresolved_no_trapping_comparison':1}


def test_report_no_candidate_density_or_score():
    x=report()
    assert x['candidate_raw_density'] is None and x['dashboard_score'] is None and x['scenario_score'] is None
    assert x['trapping_frequency_assumed'] is False


def test_source_stage_enforced():
    x=base();x['stage']='DEV-082-A3-2C'
    with pytest.raises(ValueError,match='A3-2D'):
        report(x)


def test_candidate_density_enforced():
    x=base();x['candidate_raw_density']=0.8
    with pytest.raises(ValueError,match='Cannot overwrite'):
        report(x)


def test_mismatched_row_rejected():
    x=base();x['profile_rows'][0]['quantity']=5
    with pytest.raises(ValueError,match='identity/quantity'):
        report(x)


def test_unchanged_original_report():
    x=base();report(x)
    assert 'trapping_benchmark' not in x['profile_rows'][0]

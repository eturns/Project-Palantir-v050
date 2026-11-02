"""DEV-078-AH-E1 — Combined Azog's Hunters real-army acceptance.

Author: Edward Turns (Project Lead)
All three army-wide rules in a single standard service call, without
scoring changes. No battlefield positions, attacks or dice are inferred.
"""
from pathlib import Path
from fractions import Fraction
from types import SimpleNamespace

import pytest
from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data
from pale_orcs_demands_service import PaleOrcsDemandsRequest
from morgul_arrows_service import MorgulArrowsBattlefieldRequest, MorgulArrowsShootingWound

FIXTURE = Path(__file__).parent / 'fixtures/azogs_hunters_all_options.json'
RULE_IDS = {'DG_RELENTLESS_HUNTERS', 'DG_PALE_ORCS_DEMANDS', 'DG_MORGUL_ARROWS'}


@pytest.fixture(scope='module')
def hunters():
    profiles, lists, options = load_production_azogs_hunters_data()
    load_army_rules(lists)
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army, army_list


def orc_warrior(hunters):
    from profile_classification import HeroicStatus
    return next(m for m in hunters[0].fielded_models()
                if m.configured_profile is not None
                and m.configured_profile.profile.heroic_status is HeroicStatus.WARRIOR
                and 'ORC' in {str(r).upper() for r in m.configured_profile.profile.races})


def combined_requests(hunters, *, distance=6, die=1, turn=2):
    m = orc_warrior(hunters)
    return dict(
        pale_orcs_demands_request=PaleOrcsDemandsRequest(
            attacker_model_id=m.id,
            charging_enemy_with_terror=True,
            nearest_friendly_hero_distance_inches=distance,
        ),
        morgul_arrows_request=MorgulArrowsBattlefieldRequest(
            shooting_wounds=(MorgulArrowsShootingWound(
                turn=1,
                attacker_model_id=m.id,
                target_model_id='DECLARED_ENEMY_001',
                target_is_enemy=True,
                attack_is_shooting=True,
                wound_not_prevented=True,
            ),),
            end_phase_turn=turn,
            dice_by_model_id={'DECLARED_ENEMY_001': die} if turn > 1 else {},
        ),
    )


def analyse(hunters, **kwargs):
    army, army_list = hunters
    return analyse_imported_army(
        army, army_list, army.total_points(), load_metric_thresholds(), **kwargs,
    )


def test_all_three_rules_registered_once(hunters):
    ids = [r.id for r in hunters[1].army_rules]
    assert all(ids.count(rule) == 1 for rule in RULE_IDS)


def test_combined_production_request_exposes_all_three(hunters):
    result = analyse(hunters, **combined_requests(hunters))
    assert result['mechanical_relentless_hunters'].source_rule_id == 'DG_RELENTLESS_HUNTERS'
    assert result['mechanical_pale_orcs_demands'].source_rule_id == 'DG_PALE_ORCS_DEMANDS'
    assert result['mechanical_morgul_arrows'].source_rule_id == 'DG_MORGUL_ARROWS'


def test_terrain_entitlement_covers_imported_force(hunters):
    evidence = analyse(hunters, **combined_requests(hunters))['mechanical_relentless_hunters']
    assert evidence.granted_rule_ids == ('WOODLAND_CREATURE', 'MOUNTAIN_DWELLER')
    assert set(evidence.eligible_model_ids) == {
        m.id for m in hunters[0].fielded_models() if m.counts_as_model
    }


def test_courage_modification_is_applied(hunters):
    evidence = analyse(hunters, **combined_requests(hunters))['mechanical_pale_orcs_demands']
    assert evidence.entitled and evidence.bonus == 1
    assert evidence.modified_pass_probability > evidence.baseline_pass_probability


def test_courage_proximity_boundary_without_affecting_other_rules(hunters):
    result = analyse(hunters, **combined_requests(hunters, distance=6.01))
    assert not result['mechanical_pale_orcs_demands'].entitled
    assert result['mechanical_relentless_hunters'].source_rule_id == 'DG_RELENTLESS_HUNTERS'
    assert result['mechanical_morgul_arrows'].end_phase.wounded_model_ids == ('DECLARED_ENEMY_001',)


def test_morgul_arrows_turn_two_wound_persists(hunters):
    result = analyse(hunters, **combined_requests(hunters))
    evidence = result['mechanical_morgul_arrows']
    assert evidence.state.afflicted == (('DECLARED_ENEMY_001', 1),)
    assert evidence.end_phase.rolled_model_ids == ('DECLARED_ENEMY_001',)
    assert evidence.end_phase.wounded_model_ids == ('DECLARED_ENEMY_001',)
    assert evidence.end_phase.wound_probability_per_roll == Fraction(1, 6)


def test_no_same_turn_morgul_roll(hunters):
    evidence = analyse(hunters, **combined_requests(hunters, turn=1))['mechanical_morgul_arrows']
    assert evidence.end_phase.rolled_model_ids == ()
    assert evidence.end_phase.wounded_model_ids == ()


def test_no_context_does_not_fabricate_events(hunters):
    result = analyse(hunters)
    assert 'mechanical_relentless_hunters' in result
    assert 'mechanical_pale_orcs_demands' not in result
    assert 'mechanical_morgul_arrows' not in result


def test_combined_diagnostics_are_uncalibrated(hunters):
    result = analyse(hunters, **combined_requests(hunters))
    for key in ('mechanical_relentless_hunters', 'mechanical_pale_orcs_demands',
                'mechanical_morgul_arrows'):
        assert result[key].dashboard_score is None
        assert result[key].scenario_score is None


def test_scores_remain_identical_with_combined_context(hunters):
    baseline = analyse(hunters)
    combined = analyse(hunters, **combined_requests(hunters))
    for key in ('metric_densities', 'metric_assessments', 'battlefield_assessments'):
        assert baseline[key] == combined[key]


def test_invalid_shooter_rejected_with_both_rules_active(hunters):
    req = combined_requests(hunters)
    original = req['morgul_arrows_request']
    wrong = MorgulArrowsShootingWound(
        turn=1, attacker_model_id='NOT_FIELDED', target_model_id='DECLARED_ENEMY_001',
        target_is_enemy=True, attack_is_shooting=True, wound_not_prevented=True,
    )
    req['morgul_arrows_request'] = MorgulArrowsBattlefieldRequest(
        shooting_wounds=(wrong,), end_phase_turn=2,
        dice_by_model_id=original.dice_by_model_id,
    )
    with pytest.raises(ValueError, match='not fielded'):
        analyse(hunters, **req)

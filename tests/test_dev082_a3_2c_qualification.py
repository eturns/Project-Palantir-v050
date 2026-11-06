"""DEV-082-A3-2C qualification contract tests."""
from types import SimpleNamespace as NS
import pytest
from offence_evidence_qualification import (
    qualify_offence_profile, build_qualified_offence_report,
)


def configured(pid='A', cavalry=False, rules=()):
    # Stub the configured model-type enum via a real Enum only when needed.
    from profile_classification import ModelType
    return NS(
        profile=NS(id=pid),
        effective_special_rules=tuple(NS(rule=NS(id=x)) for x in rules),
        effective_model_types={ModelType.CAVALRY} if cavalry else {ModelType.INFANTRY},
    )


def row(pid='A', qty=1, uncharged=.2, charged=.2, eligible=.2):
    return dict(profile_id=pid, quantity=qty,
                uncharged_probability=uncharged,
                charged_probability=charged,
                eligible_cavalry_charge_probability=eligible,
                unresolved_context=['charge_probability_unknown'],
                evidence_status='baseline_only_not_calibrated')


def test_non_cavalry_not_applicable():
    assert qualify_offence_profile(configured(), row())['cavalry_eligibility']['status'] == 'not_applicable'


def test_unchanged_charge_has_no_measured_effect():
    assert qualify_offence_profile(configured(), row())['charge_frequency']['status'] == 'no_measured_effect'


def test_charge_difference_requires_frequency():
    assert qualify_offence_profile(configured(), row(charged=.3, eligible=.3))['charge_frequency']['status'] == 'unresolved'


def test_cavalry_bonus_requires_eligibility():
    q = qualify_offence_profile(configured(cavalry=True), row(charged=.3, eligible=.4))
    assert q['cavalry_eligibility']['status'] == 'unresolved'


def test_cavalry_no_bonus_measured():
    q = qualify_offence_profile(configured(cavalry=True), row(charged=.3, eligible=.3))
    assert q['cavalry_eligibility']['status'] == 'no_measured_effect'


@pytest.mark.parametrize('rule', ['HATRED', 'ANCIENT_ENEMIES', 'YOU_HAVE_SOMETHING_MY_MASTER_WANTS'])
def test_target_specific_rules_require_target(rule):
    q = qualify_offence_profile(configured(rules=(rule,)), row())
    assert q['target_keywords']['status'] == 'unresolved'


def test_no_target_specific_rules_are_not_applicable():
    q = qualify_offence_profile(configured(rules=('VENOM',)), row())
    assert q['target_keywords']['status'] == 'not_applicable'


def test_trap_stays_unresolved():
    assert qualify_offence_profile(configured(), row())['trapping']['status'] == 'unresolved'


def test_weapon_selection_stays_unresolved():
    assert qualify_offence_profile(configured(), row())['weapon_selection']['status'] == 'unresolved'


def test_might_is_not_requested():
    assert qualify_offence_profile(configured(), row())['might']['status'] == 'not_requested'


def test_mismatch_profile_fails_closed():
    with pytest.raises(ValueError, match='Profile identity'):
        qualify_offence_profile(configured(pid='B'), row())


def test_out_of_range_probability_fails_closed():
    with pytest.raises(ValueError):
        qualify_offence_profile(configured(), row(eligible=1.3))


class Army:
    def __init__(self, entries):
        self.entries = entries


def make_report(rows):
    return dict(stage='DEV-082-A3-2B', candidate_raw_density=None,
                comparable=False, profile_rows=rows,
                unresolved_model_counts={'charge_probability_unknown': 3},
                legacy_raw_density=.693, dashboard_score=None, scenario_score=None)


def test_report_qualifies_without_mutating_baseline():
    existing = make_report([row(qty=1), row('B', qty=2)])
    army = Army([NS(counts_as_model=True, configured_profile=configured(), quantity=1),
                 NS(counts_as_model=True, configured_profile=configured('B', cavalry=True), quantity=2)])
    result = build_qualified_offence_report(army, report_builder=lambda a: existing)
    assert existing['stage'] == 'DEV-082-A3-2B'
    assert result['stage'] == 'DEV-082-A3-2C'
    assert result['candidate_raw_density'] is None
    assert result['qualified_unresolved_model_counts']['trapping_changes_post_duel_strikes_but_no_trap_evidence_given'] == 3
    assert result['qualified_unresolved_model_counts'].get('charged_and_uncharged_outcomes_differ_frequency_not_given') is None


def test_report_rejects_row_mismatch():
    army = Army([NS(counts_as_model=True, configured_profile=configured('B'), quantity=1)])
    with pytest.raises(ValueError, match='row order'):
        build_qualified_offence_report(army, report_builder=lambda a: make_report([row()]))


def test_report_rejects_candidate_density():
    army = Army([])
    with pytest.raises(ValueError, match='candidate scoring'):
        build_qualified_offence_report(army, report_builder=lambda a: {**make_report([]), 'candidate_raw_density':.5})

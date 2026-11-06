"""DEV-082-A3-2C — read-only qualification of real-army Offence shadow evidence.

Author: Edward Turns (Project Lead)

This is an additive audit. It never changes A3-2B's original observations,
produces no replacement density, and never assumes a trap, weapon selection,
charge frequency, target keyword or Might expenditure.
"""
from __future__ import annotations

from collections import Counter
from math import isclose, isfinite

_TARGET_KEYWORD_RULE_IDS = frozenset({
    'HATRED', 'ANCIENT_ENEMIES',
    'YOU_HAVE_SOMETHING_MY_MASTER_WANTS',
})
_CHARGE_RULE_IDS = frozenset({'PIERCING_TALONS'})


def _has_cavalry_type(configured) -> bool:
    """Respect configured form; compare against enum values, not the profile name."""
    from profile_classification import ModelType
    return ModelType.CAVALRY in configured.effective_model_types


def _rule_ids(configured) -> frozenset[str]:
    return frozenset(a.rule.id for a in configured.effective_special_rules)


def _status(value: str, reason: str) -> dict:
    return {'status': value, 'reason': reason}


def qualify_offence_profile(configured, probability_row: dict) -> dict:
    """Classify context relevance without inferring battlefield probabilities.

    `no_measured_effect` means *only* that this benchmark's two conditional
    outcomes match; it is NOT proof of a universal rule or zero charge chance.
    """
    if not isinstance(probability_row, dict):
        raise TypeError('probability_row must be dict')
    if probability_row.get('profile_id') != configured.profile.id:
        raise ValueError('Profile identity mismatch: cannot qualify wrong equipment')
    no_might = probability_row.get('uncharged_probability')
    charged = probability_row.get('charged_probability')
    cavalry = probability_row.get('eligible_cavalry_charge_probability')
    for name, value in (
        ('uncharged_probability', no_might),
        ('charged_probability', charged),
        ('eligible_cavalry_charge_probability', cavalry),
    ):
        if type(value) not in (int, float) or not isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f'Invalid {name}')

    active = _rule_ids(configured)
    is_cavalry = _has_cavalry_type(configured)
    # Strict closeness is only a comparison of measured probabilities; it
    # cannot make an unavailable context legally available.
    same_charge = isclose(no_might, charged, rel_tol=0.0, abs_tol=1e-12)
    same_cavalry = isclose(charged, cavalry, rel_tol=0.0, abs_tol=1e-12)

    qualification = {}
    qualification['charge_frequency'] = (
        _status('no_measured_effect', 'uncharged_and_charged_match_this_benchmark')
        if same_charge and same_cavalry else
        _status('unresolved', 'charged_and_uncharged_outcomes_differ_frequency_not_given')
    )
    qualification['cavalry_eligibility'] = (
        _status('not_applicable', 'configured_model_is_not_cavalry')
        if not is_cavalry else
        _status('no_measured_effect', 'eligible_and_ineligible_charge_match_this_benchmark')
        if same_cavalry else
        _status('unresolved', 'cavalry_charge_outcomes_differ_eligibility_not_given')
    )
    qualification['target_keywords'] = (
        _status('unresolved', 'attacker_has_target_keyword_dependent_wound_rule')
        if active & _TARGET_KEYWORD_RULE_IDS else
        _status('not_applicable', 'no_supported_target_keyword_wound_rule')
    )
    qualification['trapping'] = _status(
        'unresolved', 'trapping_changes_post_duel_strikes_but_no_trap_evidence_given'
    )
    # Weapon selection is deliberately left unresolved: one cannot prove
    # legal melee choices just by counting all equipped wargear items.
    qualification['weapon_selection'] = _status(
        'unresolved', 'eligible_melee_weapon_selection_not_verified'
    )
    qualification['might'] = _status(
        'not_requested', 'no_heroic_or_duel_might_allocation_in_shadow_run'
    )
    return qualification


def build_qualified_offence_report(army, *, report_builder=None) -> dict:
    """Enrich the existing A3-2B result, never replace or alter it."""
    if report_builder is None:
        from offence_real_army_comparison import build_real_army_offence_comparison
        report_builder = build_real_army_offence_comparison
    baseline = report_builder(army)
    if baseline.get('stage') != 'DEV-082-A3-2B':
        raise ValueError('Expected A3-2B real-army report')
    if baseline.get('candidate_raw_density') is not None or baseline.get('comparable') is not False:
        raise ValueError('Qualified report must not assert candidate scoring')
    source_rows = baseline.get('profile_rows')
    if not isinstance(source_rows, list):
        raise ValueError('Missing model evidence rows')
    entries = [e for e in army.entries if e.counts_as_model]
    if len(entries) != len(source_rows):
        raise ValueError('Source evidence rows do not match fielded entries')
    counts = Counter()
    rows = []
    for entry, source in zip(entries, source_rows):
        if (entry.configured_profile.profile.id != source.get('profile_id')
                or entry.quantity != source.get('quantity')):
            raise ValueError('Source row order or quantity does not match actual army')
        qualified = qualify_offence_profile(entry.configured_profile, source)
        for value in qualified.values():
            if value['status'] == 'unresolved':
                counts[value['reason']] += entry.quantity
        rows.append({**source, 'qualification': qualified})
    return {
        **baseline,
        'stage': 'DEV-082-A3-2C',
        'qualification_policy': 'explicit_applicability_no_inferred_battlefield_frequencies',
        'profile_rows': rows,
        'qualified_unresolved_model_counts': dict(sorted(counts.items())),
        'original_unresolved_model_counts': baseline['unresolved_model_counts'],
        'candidate_raw_density': None,
        'comparable': False,
        'dashboard_score': None,
        'scenario_score': None,
        'calibration_changed': False,
        'production_scoring_changed': False,
    }

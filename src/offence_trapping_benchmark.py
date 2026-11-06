"""DEV-082-A3-2E — untrapped/trapped single-wound Offence benchmark.

Author: Edward Turns (Project Lead)

Read-only conditional outcomes using the established A2 charge-state solver.
No trapping frequency, automatic weapon choice, army-level score or calibration.
"""
from __future__ import annotations

from math import isfinite


def _check_probability(value, label):
    if type(value) not in (float, int) or not isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f'{label} must be a finite probability in [0, 1]')


def compare_trapping_states(configured_profile, weapon_id: str, *, evaluator=None) -> dict:
    """Compare explicitly untrapped and trapped contexts for one selected weapon.

    `evaluator(configured_profile, weapon_id, defender_trapped)` is injectable
    for acceptance tests; default calls A2's canonical conditional evaluator.
    """
    if not isinstance(weapon_id, str) or not weapon_id.strip():
        raise ValueError('An explicit melee weapon ID is required')
    equipped = {item.id for item in configured_profile.effective_wargear}
    if weapon_id not in equipped:
        raise ValueError('Selected weapon is not equipped')
    if evaluator is None:
        from offence_charge_state_evidence import calculate_charge_state_offence_evidence
        from melee_weapon_selection import MeleeWeaponSelection
        def evaluator(profile, item_id, trapped):
            return calculate_charge_state_offence_evidence(
                profile, attacker_selection=MeleeWeaponSelection(item_id),
                defender_trapped=trapped,
            )
    untrapped = evaluator(configured_profile, weapon_id, False)
    trapped = evaluator(configured_profile, weapon_id, True)
    fields = (
        ('uncharged', 'uncharged'),
        ('charged_without_cavalry_bonus', 'charged'),
        ('charged_with_cavalry_bonus', 'eligible_cavalry_charge'),
    )
    states = []
    for attr, label in fields:
        p0, p1 = getattr(untrapped, attr), getattr(trapped, attr)
        _check_probability(p0, f'{label} untrapped')
        _check_probability(p1, f'{label} trapped')
        if p1 + 1e-12 < p0:
            raise ValueError('Trapping unexpectedly reduced kill probability')
        states.append({
            'state': label,
            'untrapped_probability': float(p0),
            'trapped_probability': float(p1),
            'absolute_improvement': float(p1 - p0),
        })
    if untrapped.weighted is not None or trapped.weighted is not None:
        raise ValueError('Unknown charge frequency cannot be weighted')
    return {
        'weapon_id': weapon_id,
        'conditional_combat_states': states,
        'trapping_frequency': None,
        'trapping_frequency_inferred': False,
        'selected_weapon_inferred': False,
        'status': 'two_explicit_trap_states_not_weighted',
        'benchmark_target': 'ordinary_single_wound',
    }


def build_trapping_qualified_offence_report(army, *, report_builder=None, evaluator=None) -> dict:
    """Augment A3-2D real-army report without changing its original results.

    Only fully catalogued single-weapon profiles are calculated. Multiple
    choices remain unresolved: no implicit selection of the strongest weapon.
    """
    if report_builder is None:
        from offence_weapon_qualification import build_weapon_qualified_offence_report
        report_builder = build_weapon_qualified_offence_report
    base = report_builder(army)
    if base.get('stage') != 'DEV-082-A3-2D':
        raise ValueError('Expected A3-2D weapon-qualified report')
    if base.get('candidate_raw_density') is not None or base.get('comparable') is not False:
        raise ValueError('Cannot overwrite or compare an army-wide Offence density')
    entries = [e for e in army.entries if e.counts_as_model]
    old_rows = base.get('profile_rows')
    if not isinstance(old_rows, list) or len(old_rows) != len(entries):
        raise ValueError('Profile rows do not match army entries')
    rows, model_status = [], {}
    for entry, row in zip(entries, old_rows):
        profile = entry.configured_profile
        if row.get('profile_id') != profile.profile.id or row.get('quantity') != entry.quantity:
            raise ValueError('Profile identity/quantity mismatch')
        weapons = row.get('weapon_options')
        if not isinstance(weapons, dict):
            raise ValueError('Missing weapon qualification')
        candidate = weapons.get('candidate_weapon_ids', ())
        if weapons.get('status') == 'single_recognised_option' and len(candidate) == 1 and not weapons.get('unclassified_wargear_ids'):
            trap = compare_trapping_states(profile, candidate[0], evaluator=evaluator)
            status = 'paired_conditional_outcomes'
        else:
            trap = None
            status = 'weapon_unresolved_no_trapping_comparison'
        model_status[status] = model_status.get(status, 0) + entry.quantity
        rows.append({**row, 'trapping_benchmark': trap, 'trapping_benchmark_status': status})
    return {
        **base,
        'stage': 'DEV-082-A3-2E',
        'profile_rows': rows,
        'trapping_benchmark_model_status_counts': dict(sorted(model_status.items())),
        'trapping_frequency_assumed': False,
        'candidate_raw_density': None,
        'comparable': False,
        'dashboard_score': None,
        'scenario_score': None,
        'calibration_changed': False,
        'production_scoring_changed': False,
    }

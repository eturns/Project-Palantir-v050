"""Project Palantír — DEV-082-A3-2D read-only melee-weapon qualification.

Author: Edward Turns (Project Lead)

The source Wargear entity has no melee category. This intentionally limited
catalogue is an audit assumption, NOT a proof of complete MESBG weapon legality.
Unknown items fail closed. No weapon choice, Might or battlefield context is
inferred, and the army-wide Offence score is never replaced.
"""
from __future__ import annotations

from math import isfinite

# Audited identifiers from data/wargear/wargear.csv. Named, special or custom
# equipment must be added deliberately after checking its actual rules.
RECOGNISED_MELEE = frozenset({
    'WG_HAND_WEAPON', 'WG_TWO_HANDED_WEAPON', 'WG_SPEAR', 'WG_WAR_SPEAR',
    'WG_MATTOCK', 'WG_CLAWS_AND_TEETH', 'WG_FANGS', 'WG_SPECTRAL_HANDS',
    'WG_MORGUL_BLADE', 'WG_ELVEN_HAND_AND_A_HALF_WEAPON',
    'WG_ELVEN_HAND_WEAPON', 'WG_LANCE', 'WG_CRUSHING_CLUB',
    'WG_STONE_FLAIL', 'WG_SCYTHE_GAUNTLETS',
})
RECOGNISED_OTHER = frozenset({
    'WG_HEAVY_DWARF_ARMOUR', 'WG_HEAVY_ARMOUR', 'WG_ARMOUR',
    'WG_LIGHT_ARMOUR', 'WG_SHIELD', 'WG_BANNER', 'WG_CROSSBOW',
    'WG_ESGAROTH_BOW', 'WG_WAR_HORN', 'WG_GREAT_BOW',
    'WG_ORC_BOW', 'WG_ELF_BOW', 'WG_ELVEN_CLOAK',
    'WG_RAPID_FIRE_BOLT_THROWER',
})


def qualify_weapon_options(configured, *, evaluator=None) -> dict:
    """List recognised choices and optionally compare verified selected states.

    An explicit selection passed to the A2 combat resolver is an *analytical
    counterfactual*. It is not evidence that the player chooses that weapon.
    No automatic optimisation or selection policy is applied.
    """
    wargear = configured.effective_wargear
    ids = tuple(item.id for item in wargear)
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate configured wargear IDs')
    unknown = tuple(sorted(set(ids) - RECOGNISED_MELEE - RECOGNISED_OTHER))
    candidates = tuple(sorted(set(ids) & RECOGNISED_MELEE))
    if unknown:
        status, reason = 'unresolved', 'unrecognised_wargear_requires_manual_classification'
    elif not candidates:
        status, reason = 'unresolved', 'no_recognised_melee_weapon_cannot_assume_unarmed'
    elif len(candidates) == 1:
        status, reason = 'single_recognised_option', 'one_catalogued_melee_option_no_player_choice_inferred'
    else:
        status, reason = 'multiple_options', 'multiple_catalogued_melee_options_no_selection_policy'
    options = []
    # Only run explicit candidate outcomes when all equipped items have a known
    # classification. Otherwise a custom rule could affect the selected state.
    if evaluator is None:
        from melee_weapon_selection import MeleeWeaponSelection
        from offence_charge_state_evidence import calculate_charge_state_offence_evidence
        def evaluator(profile, weapon_id):
            return calculate_charge_state_offence_evidence(
                profile, attacker_selection=MeleeWeaponSelection(weapon_id),
            )
    if not unknown:
        for weapon_id in candidates:
            result = evaluator(configured, weapon_id)
            probabilities = (
                result.uncharged, result.charged_without_cavalry_bonus,
                result.charged_with_cavalry_bonus,
            )
            if any(type(p) not in (float, int) or not isfinite(p) or not 0 <= p <= 1
                   for p in probabilities):
                raise ValueError('Invalid explicit-weapon conditional probability')
            if result.weighted is not None:
                raise ValueError('Weapon outcome must not assume charge probability')
            options.append({
                'weapon_id': weapon_id,
                'uncharged_probability': probabilities[0],
                'charged_probability': probabilities[1],
                'eligible_cavalry_charge_probability': probabilities[2],
            })
    return {
        'status': status,
        'reason': reason,
        'candidate_weapon_ids': list(candidates),
        'unclassified_wargear_ids': list(unknown),
        'explicit_option_outcomes': options,
        'selected_weapon_id': None,
        'automatic_choice_made': False,
    }


def build_weapon_qualified_offence_report(army, *, report_builder=None, evaluator=None) -> dict:
    """Augment A3-2C with weapon qualifications; never alter its probabilities."""
    if report_builder is None:
        from offence_evidence_qualification import build_qualified_offence_report
        report_builder = build_qualified_offence_report
    base = report_builder(army)
    if base.get('stage') != 'DEV-082-A3-2C':
        raise ValueError('Expected A3-2C report')
    if base.get('candidate_raw_density') is not None or base.get('comparable') is not False:
        raise ValueError('Candidate Offence density must remain unavailable')
    entries = [e for e in army.entries if e.counts_as_model]
    old_rows = base.get('profile_rows')
    if not isinstance(old_rows, list) or len(old_rows) != len(entries):
        raise ValueError('Profile rows do not correspond to imported army')
    rows = []
    model_counts = {}
    for entry, row in zip(entries, old_rows):
        if row.get('profile_id') != entry.configured_profile.profile.id or row.get('quantity') != entry.quantity:
            raise ValueError('Imported profile identity/quantity mismatch')
        qualification = qualify_weapon_options(entry.configured_profile, evaluator=evaluator)
        model_counts[qualification['status']] = model_counts.get(qualification['status'], 0) + entry.quantity
        # Preserve A3-2C's other qualification statuses and only reclassify
        # weapon selection based on real configured equipment evidence.
        updated = dict(row['qualification'])
        updated['weapon_selection'] = {
            'status': qualification['status'], 'reason': qualification['reason'],
        }
        rows.append({**row, 'qualification': updated, 'weapon_options': qualification})
    unresolved_counts = {}
    for entry, row in zip(entries, rows):
        for item in row['qualification'].values():
            if item['status'] == 'unresolved':
                reason = item['reason']
                unresolved_counts[reason] = unresolved_counts.get(reason, 0) + entry.quantity
    return {
        **base,
        'stage': 'DEV-082-A3-2D',
        'profile_rows': rows,
        'weapon_model_status_counts': dict(sorted(model_counts.items())),
        'qualified_unresolved_model_counts': dict(sorted(unresolved_counts.items())),
        'candidate_raw_density': None,
        'comparable': False,
        'dashboard_score': None,
        'scenario_score': None,
        'calibration_changed': False,
        'production_scoring_changed': False,
        'weapon_qualification_scope': 'audited_id_catalogue_explicit_counterfactuals_only',
    }

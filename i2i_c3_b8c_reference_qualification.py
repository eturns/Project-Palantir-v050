"""B8-C: controlled, read-only six-army reference qualification register.

This stage admits eligible real armies for EXPLORATORY calibration comparisons.
It does not approve archetypes independently, numerical anchors, production
scoring, or the whole special-rule corpus. Reports blockers rather than hiding
missing or malformed inputs.
"""
from collections import Counter
from pathlib import Path
import json

from i2i_c3_b8a_cohort_intake import FIXTURES

ROOT = Path(__file__).resolve().parent
B8A = ROOT / 'b8a_cohort_intake.json'
B8B5 = ROOT / 'b8b5_real_army_integration.json'

METRIC_POLICY = {
    'offence': 'exploratory_benchmark_only',
    'defence': 'exploratory_benchmark_only',
    'mobility': 'exploratory_benchmark_only',
    'shooting': 'exploratory_benchmark_only',
    'courage': 'exploratory_benchmark_only',
    'magic': 'partial_evidence_only',
    'control': 'requires_battle_context',
    'command': 'requires_battle_context',
    'objective': 'requires_scenario_context',
    'hero_hunting': 'requires_named_target',
}

LIMITATIONS = {
    'dol_guldur': ('terror_and_resurrection_context', 'magic_resource_and_casting_limits'),
    'azogs_hunters': ('conditional_enemy_keywords_and_charge_state',),
    'pits_of_dol_guldur': ('conditional_enemy_keywords_and_charge_state',),
    'rangers_of_mirkwood': ('woodland_creature_knife_fighter_sharpshooter_runtime_link',),
    'five_armies': ('bow_exchange_verified_but_other_hero_rules_not_fully_audited',),
    'iron_hills': ('chariot_platform_physical_behaviour_unverified', 'rule_assignment_completeness_review'),
}


def read_json(path):
    data = path.read_bytes()
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        return json.loads(data.decode('utf-16'))
    if data[:4].count(b'\x00') >= 1:
        # PowerShell redirection on some Windows installations produces UTF-16.
        return json.loads(data.decode('utf-16-le'))
    return json.loads(data.decode('utf-8-sig'))


def qualify(intake, integration):
    errors = []
    if intake.get('stage') != 'B8-A' or integration.get('stage') != 'B8-B5':
        errors.append('wrong_evidence_stage')
    if intake.get('intake_passed') != 6 or intake.get('candidates') != 6:
        errors.append('six_army_intake_not_complete')
    if integration.get('armies_imported') != 6 or integration.get('import_errors'):
        errors.append('six_army_runtime_import_not_complete')
    if not isinstance(intake.get('results'), list) or len(intake['results']) != 6:
        errors.append('six_intake_records_required')
    if not isinstance(integration.get('checks'), list):
        errors.append('runtime_checks_missing')
    checks = integration.get('checks', [])
    if integration.get('summary', {}).get('blocked', -1) != 0 or any(
        c.get('status') == 'blocked' for c in checks
    ):
        errors.append('runtime_blockers_present')
    if any(c.get('status') not in ('verified', 'conditional') for c in checks):
        errors.append('unrecognised_runtime_check_status')
    if not checks:
        errors.append('empty_runtime_evidence')
    if integration.get('calibration_anchors_approved') is not False:
        errors.append('unsafe_existing_anchor_approval')

    records = {r.get('key'): r for r in intake.get('results', []) if isinstance(r, dict)}
    if set(records) != set(FIXTURES):
        errors.append('reference_army_identity_mismatch')
    rows = []
    for key, (filename, alignment, archetype) in FIXTURES.items():
        record = records.get(key, {})
        issues = []
        if record.get('status') != 'intake_passed' or record.get('issues'):
            issues.append('intake_not_passed')
        if record.get('alignment') != alignment or record.get('proposed_archetype') != archetype:
            issues.append('cohort_classification_mismatch')
        if Path(record.get('file', '')).name != filename:
            issues.append('fixture_name_mismatch')
        if not isinstance(record.get('declared_points'), int) or not 695 <= record['declared_points'] <= 700:
            issues.append('points_out_of_reference_window')
        if record.get('imported_points') != record.get('declared_points'):
            issues.append('imported_points_mismatch')
        if record.get('imported_models') != record.get('models'):
            issues.append('imported_models_mismatch')
        if record.get('archetype_review_approved') is not False:
            issues.append('prior_unjustified_archetype_approval')
        rows.append({
            'army': key, 'alignment': alignment, 'proposed_archetype': archetype,
            'points': record.get('declared_points'), 'models': record.get('models'),
            'candidate_status': 'provisional_reference' if not issues and not errors else 'blocked',
            'candidate_issues': issues,
            'metric_permissions': dict(METRIC_POLICY),
            'material_limitations': list(LIMITATIONS[key]),
            'independent_archetype_approval': False,
            'rulebook_profile_completeness_approved': False,
            'full_mechanical_qualification_approved': False,
        })
    balance = Counter(row['alignment'] for row in rows if row['candidate_status'] == 'provisional_reference')
    distinct = len({row['proposed_archetype'] for row in rows
                    if row['candidate_status'] == 'provisional_reference'})
    if balance != Counter({'Good': 3, 'Evil': 3}) or distinct < 4:
        errors.append('population_balance_or_archetype_diversity_not_met')
    if errors:
        for row in rows:
            row['candidate_status'] = 'blocked'
    return {
        'stage': 'B8-C', 'scope': 'provisional_reference_decision',
        'status': 'provisional_evidence_qualified' if not errors else 'blocked',
        'armies': rows, 'qualification_errors': errors,
        'provisional_references': sum(row['candidate_status'] == 'provisional_reference' for row in rows),
        'candidate_count': len(rows),
        'independent_archetype_review_pending': True,
        'rulebook_assignment_audit_pending': True,
        'full_mechanical_qualification_pending': True,
        'numerical_calibration_permitted': False,
        'calibration_anchors_approved': False,
        'production_scoring_modified': False,
        'notes': [
            'Provisional reference status allows read-only diagnostic comparisons only.',
            'A benchmark-level interface is not proof of per-rule completeness.',
            'No metric values or missing-effect zeroes have been invented.',
            'Chariot platform and contextual abilities remain explicitly unapproved.',
        ],
    }


def main():
    # Earlier intake command prints JSON but does not automatically save it.
    # Run it and capture output when this file does not exist.
    missing = [str(p.name) for p in (B8A, B8B5) if not p.is_file()]
    if missing:
        print(json.dumps({'stage': 'B8-C', 'status': 'missing_evidence_files',
                          'required_files': missing}, indent=2))
        raise SystemExit(2)
    print(json.dumps(qualify(read_json(B8A), read_json(B8B5)), indent=2))


if __name__ == '__main__':
    main()

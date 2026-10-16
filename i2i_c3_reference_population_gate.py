"""DEV-077S-I2-I-C3-D5: conservative, read-only reference population gate.

No scores, weights, benchmark anchors, or scenario results are produced.
Reference alignment/archetype metadata must be supplied explicitly, not inferred
from roster name or the analysis engine.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

METRICS = ('offence', 'defence', 'mobility', 'magic', 'shooting',
           'courage', 'control', 'command', 'objective', 'hero_hunting')

# D5 research policy, not an agreed production calibration contract.
TARGET_POINTS = 700
POINT_TOLERANCE = 5  # 695 through 700 inclusive; no over-limit armies
MIN_TOTAL = 6
MIN_PER_ALIGNMENT = 3
MIN_ARCHETYPES = 4
MIN_METRIC_ARMIES = 6
MIN_DISTINCT_VALUES = 3


@dataclass(frozen=True)
class ReferenceDescriptor:
    army_key: str
    alignment: str
    archetype: str
    evidence_path: str

    def __post_init__(self):
        if not self.army_key.strip() or not self.archetype.strip() or not self.evidence_path.strip():
            raise ValueError('Reference identity, archetype and evidence path are required')
        if self.alignment not in ('Good', 'Evil'):
            raise ValueError('Alignment must be Good or Evil')


def _finite_number(value):
    return (isinstance(value, (float, int)) and not isinstance(value, bool)
            and math.isfinite(value))


def load_evidence(path: str | Path) -> dict:
    with Path(path).open(encoding='utf-8') as f:
        doc = json.load(f)
    if not isinstance(doc, dict) or not isinstance(doc.get('measurements'), list):
        raise ValueError(f'Invalid evidence document: {path}')
    if doc.get('production_scoring_enabled') is not False or doc.get('reference_anchors_approved') is not False:
        raise ValueError(f'Scoring/anchor state is not explicitly disabled: {path}')
    if type(doc.get('points')) is not int or doc['points'] <= 0:
        raise ValueError(f'Invalid army points: {path}')
    if not isinstance(doc.get('analysis_commit'), str) or not doc['analysis_commit']:
        raise ValueError(f'Missing analysis commit: {path}')
    measurements = doc['measurements']
    if [m.get('metric') for m in measurements] != list(METRICS):
        raise ValueError(f'Ten canonical ordered metrics required: {path}')
    for m in measurements:
        status, value = m.get('availability'), m.get('value')
        if status not in ('available', 'partial', 'unavailable'):
            raise ValueError('Invalid evidence availability')
        if status == 'unavailable' and value is not None:
            raise ValueError('Unavailable metric must not have numeric value')
        if status == 'available' and not _finite_number(value):
            raise ValueError('Available metric must be finite numeric')
        if status == 'partial' and value is not None and not _finite_number(value):
            raise ValueError('Partial numeric value must be finite')
        if status == 'partial' and not m.get('unresolved'):
            raise ValueError('Partial metric requires unresolved conditions')
        if not all(isinstance(m.get(k), str) and m[k].strip()
                   for k in ('unit', 'population', 'provenance')):
            raise ValueError('Evidence unit/population/provenance required')
    return doc


def assess_population(descriptors: tuple[ReferenceDescriptor, ...],
                      *, target_points: int = TARGET_POINTS) -> dict:
    """Diagnostic readiness only. No proposed anchors or approval flags are set."""
    if type(target_points) is not int or target_points <= 0:
        raise ValueError('target_points must be a positive integer')
    if len({d.army_key for d in descriptors}) != len(descriptors):
        raise ValueError('Duplicate army keys are not independent references')
    records = []
    for d in descriptors:
        doc = load_evidence(d.evidence_path)
        if doc.get('army_key') != d.army_key:
            raise ValueError(f'Identity mismatch for {d.army_key}')
        records.append((d, doc))
    blockers = []
    commits = sorted({doc['analysis_commit'] for _, doc in records})
    if len(commits) > 1:
        blockers.append('mixed_analysis_commits')
    exact = [(d, doc) for d, doc in records
             if target_points - POINT_TOLERANCE <= doc['points'] <= target_points]
    if len(exact) < MIN_TOTAL:
        blockers.append(f'needs_{MIN_TOTAL}_target_point_armies')
    alignments = Counter(d.alignment for d, _ in exact)
    for side in ('Good', 'Evil'):
        if alignments[side] < MIN_PER_ALIGNMENT:
            blockers.append(f'needs_{MIN_PER_ALIGNMENT}_{side.lower()}_target_point_armies')
    archetypes = sorted({d.archetype for d, _ in exact})
    if len(archetypes) < MIN_ARCHETYPES:
        blockers.append(f'needs_{MIN_ARCHETYPES}_target_point_archetypes')
    reports = []
    for metric in METRICS:
        usable = [(d, next(m for m in doc['measurements'] if m['metric'] == metric))
                  for d, doc in exact]
        complete = [(d, m) for d, m in usable if m['availability'] == 'available']
        partial = sum(m['availability'] == 'partial' for _, m in usable)
        unavailable = sum(m['availability'] == 'unavailable' for _, m in usable)
        signatures = {(m['unit'], m['population'], tuple(m.get('assumptions', [])))
                      for _, m in complete}
        values = [float(m['value']) for _, m in complete]
        distinct = len(set(values))
        nonzero = sum(v != 0 for v in values)
        metric_blockers = []
        if len(complete) < MIN_METRIC_ARMIES:
            metric_blockers.append('insufficient_complete_target_point_observations')
        if len(signatures) > 1:
            metric_blockers.append('incompatible_measurement_definitions')
        if distinct < MIN_DISTINCT_VALUES:
            metric_blockers.append('insufficient_numeric_variation')
        if metric == 'shooting' and nonzero < 3:
            metric_blockers.append('insufficient_nonzero_shooting_observations')
        if len({d.alignment for d, _ in complete}) < 2:
            metric_blockers.append('both_alignments_not_represented')
        reports.append({
            'metric': metric, 'complete_target_point': len(complete),
            'partial_target_point': partial, 'unavailable_target_point': unavailable,
            'distinct_numeric_values': distinct, 'nonzero_values': nonzero,
            'definition_compatible': len(signatures) <= 1,
            'blockers': metric_blockers,
            'ready_for_anchor_review': not blockers and not metric_blockers,
        })
    return {
        'development': 'DEV-077S-I2-I-C3-D5',
        'purpose': 'reference_population_quality_diagnostic_only',
        'research_policy': {'target_points': target_points,
                            'min_reference_points': target_points - POINT_TOLERANCE,
                            'max_reference_points': target_points,
                            'min_armies': MIN_TOTAL,
                            'min_per_alignment': MIN_PER_ALIGNMENT,
                            'min_archetypes': MIN_ARCHETYPES},
        'input_armies': len(records), 'target_point_armies': len(exact),
        'excluded_mixed_points': [
            {'army_key': d.army_key, 'points': doc['points']}
            for d, doc in records if not (target_points - POINT_TOLERANCE <= doc['points'] <= target_points)
        ],
        'alignments': dict(alignments), 'archetypes': archetypes,
        'analysis_commits': commits, 'population_blockers': blockers,
        'metrics': reports, 'anchors_approved': False,
        'production_scoring_enabled': False, 'scenario_scoring_changed': False,
    }


DEFAULT_REFERENCES = (
    ('dol_guldur_elite', 'Evil', 'elite_magic', 'dol_guldur_700_evidence.json'),
    ('iron_hills', 'Good', 'elite_infantry', 'iron_hills_evidence.json'),
    ('garrison_of_dale', 'Good', 'infantry', 'garrison_of_dale_evidence.json'),
    ('five_armies', 'Good', 'mixed_elite', 'five_armies_evidence.json'),
)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence-dir', default='docs/validation/i2i_c3')
    p.add_argument('--output', default=None)
    args = p.parse_args(argv)
    directory = Path(args.evidence_dir)
    descriptors = tuple(ReferenceDescriptor(k, side, archetype, str(directory / name))
                        for k, side, archetype, name in DEFAULT_REFERENCES)
    report = assess_population(descriptors)
    rendered = json.dumps(report, indent=2) + '\n'
    if args.output:
        out = Path(args.output)
        if out.exists():
            p.error(f'Refusing to overwrite existing report: {out}')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding='utf-8')
    print(rendered, end='')
    return report


if __name__ == '__main__':
    main()

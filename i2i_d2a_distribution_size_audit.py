"""DEV-077S-I2-I-D2-A: six-army distribution and model-count audit.

Read-only descriptive statistics. Does not fit normalisation or calibration
thresholds, change scoring, or infer game strength from unapproved metrics.
"""
import json
import math
from pathlib import Path
from statistics import mean, median, pstdev

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'i2i_d1_measurement_matrix.json'
OUTPUT = ROOT / 'i2i_d2a_distribution_size_report.json'
METRICS = ('offence', 'defence', 'mobility', 'shooting', 'courage')


def read_json(path):
    raw = Path(path).read_bytes()
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        return json.loads(raw.decode('utf-16'))
    if raw[:8].count(b'\x00') >= 2:
        return json.loads(raw.decode('utf-16-le'))
    return json.loads(raw.decode('utf-8-sig'))


def pearson(xs, ys):
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    ax, ay = mean(xs), mean(ys)
    numerator = sum((x-ax)*(y-ay) for x, y in zip(xs, ys))
    dx = sum((x-ax)**2 for x in xs)
    dy = sum((y-ay)**2 for y in ys)
    if dx <= 0 or dy <= 0:
        return None
    return numerator / math.sqrt(dx*dy)


def analyse(d1, b8a):
    if d1.get('stage') != 'I2-I-D1' or d1.get('status') != 'matrix_complete':
        raise ValueError('D1 matrix_complete evidence required')
    if b8a.get('stage') != 'B8-A' or b8a.get('intake_passed') != 6:
        raise ValueError('Six-army B8-A intake evidence required')
    rows = d1['rows']
    if len(rows) != 6 or len({r['army'] for r in rows}) != 6:
        raise ValueError('D1 must contain six unique armies')
    intake = {r['key']: r for r in b8a['results']}
    if set(intake) != {r['army'] for r in rows}:
        raise ValueError('D1 and B8-A army identities differ')
    validated=[]
    for row in rows:
        i = intake[row['army']]
        if i['status'] != 'intake_passed' or i['declared_points'] != row['points']:
            raise ValueError(f'Intake mismatch: {row["army"]}')
        count=i['models']
        pts=row['points']
        if not isinstance(count,int) or count <= 0 or pts <= 0:
            raise ValueError('Positive points and model count required')
        vals={}
        for metric in METRICS:
            obj=row['measurements'][metric]
            if obj is None or obj.get('approved') is not False:
                raise ValueError(f'Unapproved D1 mechanical value required: {metric}')
            number=obj['value']
            if isinstance(number,bool) or not isinstance(number,(int,float)) or not math.isfinite(number):
                raise ValueError(f'Finite D1 value required: {metric}')
            vals[metric]=float(number)
        validated.append({'army': row['army'], 'archetype': row['proposed_archetype'],
                          'alignment': row['alignment'], 'points':pts, 'models':count,
                          'values':vals})
    distributions={}
    for metric in METRICS:
        ordered=sorted(validated,key=lambda r:(-r['values'][metric],r['army']))
        vals=[r['values'][metric] for r in validated]
        distributions[metric]={
            'mean':mean(vals), 'median':median(vals), 'min':min(vals),
            'max':max(vals), 'range':max(vals)-min(vals), 'population_stddev':pstdev(vals),
            'descending_rank': [{'army':r['army'],'value':r['values'][metric]} for r in ordered],
            'model_count_pearson_descriptive_only':pearson([r['models'] for r in validated],vals),
        }
    # Density is a sum per 100 points. Reverse that denominator and divide
    # by count to expose the implicit average per-model survival contribution.
    defence=[]
    for r in validated:
        density=r['values']['defence']
        total=density*r['points']/100
        defence.append({'army':r['army'],'models':r['models'],
                        'survival_density_per_100_points':density,
                        'implied_total_survival_contribution':total,
                        'implied_mean_survival_contribution_per_model':total/r['models']})
    return {'stage':'I2-I-D2-A','status':'distribution_audit_complete',
            'armies':len(validated),'metrics':list(METRICS),
            'distributions':distributions,
            'defence_size_decomposition':defence,
            'defence_density_vs_model_count_correlation':distributions['defence']['model_count_pearson_descriptive_only'],
            'limitations':[
                'Six deliberately selected armies are not a representative statistical sample.',
                'Correlation with six rosters cannot establish causation.',
                'Per-model Defence decomposition is algebraic, not an independent survival simulation.',
                'No opponent, movement, terrain or shooting benchmark varied in D2-A; D2-B must test those.',
                'Different capability units must never be directly averaged or ranked as one scalar.',
                'Chariot, contextual special rules and calibration gate remain unapproved.'
            ],
            'numerical_calibration_permitted':False,
            'calibration_thresholds_fitted':False,
            'calibration_anchors_approved':False,
            'production_scoring_modified':False}


def main():
    result=analyse(read_json(INPUT),read_json(ROOT/'b8a_cohort_intake.json'))
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()

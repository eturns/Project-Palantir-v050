"""Guarded opt-in integration into profile_offensive_combat_score.py."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'src' / 'profile_offensive_combat_score.py'

IMPORT_ANCHOR = 'from fractions import Fraction\n'
IMPORT_ADD = '''from gundabad_goblin_crew import GoblinCrewCombatContext
from gundabad_goblin_crew_combat import combined_goblin_crew_kill_probability
'''
ARG_ANCHOR = '    charge_probability: float = 1.0,\n) -> float:'
ARG_REPLACEMENT = '    charge_probability: float = 1.0,\n    goblin_crew_context: GoblinCrewCombatContext | None = None,\n) -> float:'
RET_ANCHOR = '''    return (
        duel_result.attacker_win_probability
        * float(
            probability_of_defeating_benchmark,
        )
    )'''
RET_REPLACEMENT = '''    if goblin_crew_context is not None:
        if not isinstance(profile, ConfiguredProfile):
            raise ValueError("Goblin Crew context requires a configured attacker.")
        if post_prevention_effect is not PostPreventionEffect.NONE:
            raise ValueError("Goblin Crew combined evidence cannot model post-prevention effects.")
        probability_of_defeating_benchmark = combined_goblin_crew_kill_probability(
            profile,
            troll_wound_distribution=wound_distribution,
            troll_wounds_per_success=wounds_per_successful_strike,
            target_wounds=benchmark.wounds,
            target_defence=benchmark.defence,
            context=goblin_crew_context,
        )

    return (
        duel_result.attacker_win_probability
        * float(
            probability_of_defeating_benchmark,
        )
    )'''


def main():
    source = TARGET.read_text(encoding='utf-8')
    if 'goblin_crew_context: GoblinCrewCombatContext | None = None' in source:
        if 'combined_goblin_crew_kill_probability(' in source:
            print('C6-C2 already applied; no changes.')
            return
        raise ValueError('Partial C6-C2 patch found; no changes made.')
    for old in (IMPORT_ANCHOR, ARG_ANCHOR, RET_ANCHOR):
        if source.count(old) != 1:
            raise ValueError(f'Expected a unique integration anchor but found {source.count(old)}: {old[:72]!r}. No changes made.')
    updated = source.replace(IMPORT_ANCHOR, IMPORT_ANCHOR + IMPORT_ADD, 1)
    updated = updated.replace(ARG_ANCHOR, ARG_REPLACEMENT, 1)
    updated = updated.replace(RET_ANCHOR, RET_REPLACEMENT, 1)
    backup = TARGET.with_suffix('.py.c6c2.bak')
    if not backup.exists():
        shutil.copy2(TARGET, backup)
    TARGET.write_text(updated, encoding='utf-8')
    print('C6-C2 opt-in integration applied:', TARGET)
    print('Backup:', backup)


if __name__ == '__main__':
    main()

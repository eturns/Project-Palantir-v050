"""Guarded C6-C1 integration: Strength 10 only for Metal Gauntlets Strikes."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'src' / 'configured_wound_probability.py'
OLD_IMPORT = 'from morgul_blade_combat_values import ('
NEW_IMPORT = ('from gundabad_metal_gauntlets import has_metal_gauntlets\n'
              'from wound_attack_type import WoundAttackType\n' + OLD_IMPORT)
OLD = '''    target = get_wound_target(
        strength=attack_strength,'''
NEW = '''    # Metal Gauntlets change melee Strikes, not base Strength or other hits.
    if (
        has_metal_gauntlets(attacker)
        and (context is None or context.attack_type is WoundAttackType.STRIKE)
    ):
        attack_strength = 10

    target = get_wound_target(
        strength=attack_strength,'''


def main():
    source = TARGET.read_text(encoding='utf-8')
    if NEW in source:
        print('C6-C1 already applied: no changes.')
        return
    if source.count(OLD) != 1 or source.count(OLD_IMPORT) != 1:
        raise ValueError('Unexpected current source layout; no changes made. Share configured_wound_probability.py for tailored patch.')
    if 'from gundabad_metal_gauntlets import' in source:
        raise ValueError('Existing Metal Gauntlets integration detected; no changes made.')
    updated = source.replace(OLD_IMPORT, NEW_IMPORT, 1).replace(OLD, NEW, 1)
    backup = TARGET.with_suffix('.py.c6c1.bak')
    if not backup.exists():
        shutil.copy2(TARGET, backup)
    TARGET.write_text(updated, encoding='utf-8')
    print('C6-C1 integrated:', TARGET)
    print('Backup:', backup)


if __name__ == '__main__':
    main()

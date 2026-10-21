"""Safe opt-in integration hook; leaves existing shooting metrics unchanged."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'src' / 'army_shooting_capability.py'
MARKER = 'from gundabad_catapult_army_evidence import calculate_catapult_army_shooting_evidence'


def main():
    text = TARGET.read_text(encoding='utf-8')
    if MARKER in text:
        print('C6-C3 already connected: no changes')
        return
    anchor = 'from fractions import Fraction\n'
    if text.count(anchor) != 1:
        raise ValueError('Unexpected shooting module layout, no changes made')
    if 'gundabad_catapult_army_evidence' in text:
        raise ValueError('Potential existing Catapult integration: inspect manually')
    backup = TARGET.with_suffix('.py.c6c3.bak')
    if not backup.exists():
        shutil.copy2(TARGET, backup)
    TARGET.write_text(text.replace(anchor, anchor + '\n' + MARKER + '\n', 1), encoding='utf-8')
    print('C6-C3 explicit-context evidence exported through:', TARGET)
    print('Existing output-density/dashboard logic unchanged')
    print('Backup:', backup)


if __name__ == '__main__':
    main()

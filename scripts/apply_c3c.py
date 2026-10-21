"""Safely install C3-C on the current LOCAL configured_profile.py.

Produces a complete updated src/configured_profile.py in place, retaining
uncommitted local edits rather than replacing the file with an old Git copy.
"""
from pathlib import Path
import ast

path = Path('src/configured_profile.py')
if not path.is_file():
    raise SystemExit('Run from the Project Palantir repository root.')
source = path.read_text(encoding='utf-8')
needle = '''        if self.effective_mount is not None:
            return max(
                self.profile.attacks,
                self.effective_mount.attacks,
            )

        return self.profile.attacks
'''
replacement = '''        # DEV-077-GUN-C3-C: The Gundabad Troll's Scythe Gauntlets
        # replace its Crushing Club and grant an Attacks value of 4.
        # Evaluate configured equipment, never an army-wide bonus.
        if self.profile.id == "GUNDABAD_TROLL" and any(
            wargear.id == "WG_SCYTHE_GAUNTLETS"
            for wargear in self.effective_wargear
        ):
            return 4

        if self.effective_mount is not None:
            return max(
                self.profile.attacks,
                self.effective_mount.attacks,
            )

        return self.profile.attacks
'''
if 'DEV-077-GUN-C3-C' in source:
    print('C3-C already installed; no change made.')
elif source.count(needle) != 1:
    raise SystemExit('Unexpected configured_profile.py structure; no changes made. Share the current file for a safe full replacement.')
else:
    updated = source.replace(needle, replacement, 1)
    ast.parse(updated)
    backup = path.with_name('configured_profile.pre_c3c.bak')
    if backup.exists():
        raise SystemExit(f'Backup already exists at {backup}; no changes made.')
    backup.write_text(source, encoding='utf-8')
    path.write_text(updated, encoding='utf-8')
    print(f'Updated {path}; backup: {backup}')

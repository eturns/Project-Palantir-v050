"""Idempotent guarded addition of C6-C4 evidence interface (no rating changes)."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "src" / "mobility_integration_contract.py"
MARKER = "# DEV-077-GUN-C6-C4: optional War Beast Trample contact evidence"
APPEND = '''\n\n''' + MARKER + '''
from gundabad_trample_movement_evidence import build_trample_movement_evidence


def build_troll_brute_trample_movement_evidence(
    combatant, *, is_trampling: bool, contacts: tuple
):
    """Diagnostic-only bridge; never changes calibrated mobility measures."""
    return build_trample_movement_evidence(
        combatant, is_trampling=is_trampling, contacts=contacts,
    )
'''


def main():
    original = FILE.read_text(encoding="utf-8")
    if MARKER in original:
        if original.count(MARKER) != 1:
            raise ValueError("Duplicate C6-C4 marker in target")
        print("C6-C4 already applied; no change")
        return
    if "def build_mobility_integration_contract(" not in original:
        raise ValueError("Unexpected mobility contract; no modification made")
    if "build_troll_brute_trample_movement_evidence" in original:
        raise ValueError("Existing alternative integration detected; no modification made")
    backup = FILE.with_suffix(".py.c6c4.bak")
    if not backup.exists():
        shutil.copy2(FILE, backup)
    FILE.write_text(original.rstrip() + APPEND, encoding="utf-8")
    print("C6-C4 integrated:", FILE)
    print("Backup:", backup)


if __name__ == "__main__":
    main()

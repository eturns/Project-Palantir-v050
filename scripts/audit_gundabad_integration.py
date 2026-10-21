"""Read-only DEV-077-GUN-C6-C local call-site audit; no repo modifications.

Run from repository root: py -3.14 scripts/audit_gundabad_integration.py
"""
from __future__ import annotations
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TARGETS = {
    "gundabad_troll_brute_trample",
    "gundabad_metal_gauntlets",
    "gundabad_catapult_shooting",
    "gundabad_goblin_crew",
}
OUTPUTS = (
    "army_shooting_capability.py", "profile_offensive_combat_score.py",
    "configured_wound_probability.py", "army_offence_capability.py",
    "hero_hunting_melee.py", "services/army_analysis_service.py",
    "ranged_weapon_resolver.py", "shooting_eligibility.py",
)


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Expected src directory at {SRC}")
    print("DEV-077-GUN-C6-C — READ-ONLY INTEGRATION AUDIT")
    print("Repository:", ROOT)
    files = sorted(SRC.rglob("*.py"))
    module_paths = {p.stem: p for p in files}
    for module in sorted(TARGETS):
        p = module_paths.get(module)
        print(f"\n[{module}] present: {bool(p)}")
        if not p:
            continue
        tree = ast.parse(p.read_text(encoding="utf-8-sig"), filename=str(p))
        functions = [n.name for n in ast.walk(tree)
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        print("  API:", ", ".join(functions[:30]) or "(none)")
        consumers = []
        for other in files:
            if other == p:
                continue
            try:
                code = other.read_text(encoding="utf-8-sig")
                other_tree = ast.parse(code, filename=str(other))
            except (UnicodeError, SyntaxError):
                continue
            imports = [n for n in ast.walk(other_tree) if isinstance(n, ast.ImportFrom)
                       and n.module and (n.module == module or n.module.endswith("." + module))]
            imports += [n for n in ast.walk(other_tree) if isinstance(n, ast.Import)
                        and any(a.name == module or a.name.endswith("." + module) for a in n.names)]
            if imports:
                consumers.append((other.relative_to(SRC), sorted({n.lineno for n in imports})))
        if consumers:
            for path, lines in consumers:
                print(f"  IMPORTED BY: {path} (lines {','.join(map(str, lines))})")
        else:
            print("  NO SOURCE IMPORTS FOUND — resolver may be isolated")
    print("\n[IMPORTANT ANALYSIS PATHS]")
    for relative in OUTPUTS:
        p = SRC / relative
        if not p.exists():
            print(f"  NOT FOUND: {relative}")
            continue
        code = p.read_text(encoding="utf-8-sig")
        found = [name for name in TARGETS if name in code]
        print(f"  {relative}: Gundabad resolver references: {', '.join(sorted(found)) or 'none'}")
    print("\nNOTE: imports/references are evidence of potential connection, NOT proof")
    print("of runtime invocation or correct scoring. This script changes no files.")


if __name__ == "__main__":
    main()

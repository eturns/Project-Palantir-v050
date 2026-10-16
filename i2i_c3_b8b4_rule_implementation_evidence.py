"""DEV-077S-I2-I-C3-D7-B8-B4: read-only local implementation evidence.

Reads B8-B3 report and local Python source/tests. Source references are
candidates, NEVER proof of correct execution. Requiring direct test execution
and manual functional review remains an explicit approval gate.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "src"
TESTS = ROOT / "tests"
INVENTORY = ROOT / "b8b3_profile_rule_report.json"
EXCLUDE = ("special_rule", "rule_loader", "profile_special", "unified_capability_inventory")
# Search rule IDs and human-readable variants, never fabricated synonyms.
def tokens(rule_id):
    return (rule_id.upper(), rule_id.replace("_", " ").upper())

def scan(root, *, exclude=()):
    if not root.exists():
        return {}, [f"missing_directory:{root.name}"]
    files = {}
    errors = []
    for path in sorted(root.rglob("*.py")):
        if any(name in path.stem for name in exclude):
            continue
        try:
            files[path.relative_to(ROOT).as_posix()] = path.read_text(
                encoding="utf-8-sig", errors="replace"
            ).upper()
        except OSError as exc:
            errors.append(f"read_failed:{path}:{exc}")
    return files, errors

def matching_paths(rule_id, files):
    variants = tokens(rule_id)
    # exact word boundary: avoid matching prefixes of longer rule IDs
    return [path for path, contents in files.items()
            if any(re.search(r"(?<![A-Z0-9_])" + re.escape(t) +
                             r"(?![A-Z0-9_])", contents) for t in variants)]

def read_inventory(path=INVENTORY):
    """Read JSON produced by PowerShell redirects (UTF-8 or UTF-16)."""
    data = Path(path).read_bytes()
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        content = data.decode("utf-16")
    elif data.startswith(b"\xef\xbb\xbf"):
        content = data.decode("utf-8-sig")
    else:
        content = data.decode("utf-8")
    return json.loads(content)


def build_report(inventory=None, *, source=None, tests=None):
    if inventory is None:
        inventory = read_inventory()
    if source is None:
        source, src_errors = scan(SOURCE, exclude=EXCLUDE)
    else:
        src_errors = []
    if tests is None:
        tests, test_errors = scan(TESTS, exclude=("profile_special_rule_assignment",))
    else:
        test_errors = []
    exposures = inventory["cross_army_verification_queue"]
    results = []
    for rule in exposures:
        name = rule["rule_id"]
        src = matching_paths(name, source)
        test = matching_paths(name, tests)
        # Even with both source & tests, correctness remains UNVERIFIED.
        evidence = ("source_and_tests_found" if src and test else
                    "source_only" if src else "tests_only" if test else
                    "no_explicit_references_found")
        results.append({
            "rule_id": name,
            "armies_affected": rule["armies_affected"],
            "assignment_exposures": rule["model_exposures"],
            "evidence_discovery": evidence,
            "candidate_source_files": src,
            "candidate_test_files": test,
            "runtime_mechanical_verification": "not_verified",
            "manual_rulebook_comparison": "pending",
            "calibration_approved": False,
        })
    return {
        "stage": "B8-B4",
        "scope": "local_source_and_test_evidence_discovery",
        "rules": results,
        "rules_scanned": len(results),
        "errors": src_errors + test_errors,
        "caveats": [
            "Text references and passing tests do not alone prove correct mechanical impact.",
            "Assignment exposure counts can double-count model/rule parameters.",
            "Missing references are investigation candidates, not definitive missing implementations.",
            "Army-list special rules and rulebook assignment completeness are separate audits.",
        ],
        "full_special_rules_approved": False,
        "archetype_review_approved": False,
        "calibration_anchors_approved": False,
        "production_scoring_modified": False,
    }

if __name__ == "__main__":
    print(json.dumps(build_report(), indent=2))

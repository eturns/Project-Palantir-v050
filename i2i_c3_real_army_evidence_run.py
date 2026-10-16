"""DEV-077S-I2-I-C3-D: regenerate raw mechanical evidence from a real MESBG fixture.

Install at repository root. Invoke with --fixture and --output. The established
Palantir loader and existing C1/C2 contracts are reused; no scoring writes.
"""
import argparse
import hashlib
import json
from fractions import Fraction
from math import isfinite
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))


def validate_paths(fixture, output):
    fixture, output = Path(fixture).resolve(), Path(output).resolve()
    if not fixture.is_file() or fixture.suffix.lower() != '.json':
        raise ValueError("Input must be an existing JSON roster fixture")
    if output == fixture or output.exists():
        raise ValueError("Output must be new and distinct from fixture")
    return fixture, output


def normalise_raw_shooting_for_extractor(value):
    """Convert the shooting engine's exact Fraction into an extractor float.

    This converts representation only: it does not apply scoring normalisation.
    Non-finite or unsupported values are rejected instead of silently lost.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise TypeError("Raw shooting output must be a finite Fraction or number")
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError("Raw shooting output cannot be represented finitely") from exc
    if not isfinite(number):
        raise ValueError("Raw shooting output must be finite")
    return number


def build_evidence_document(*, fixture, army_key, result, analysis_commit,
                            raw_shooting, source_revision="current_roster"):
    """Create a research-only record from a *fresh* production analysis result."""
    from unified_real_army_measurements import extract_mechanical_army_snapshot
    from unified_mechanical_provider_adapters import (
        ProviderEvidenceBundle, extend_mechanical_army_snapshot,
    )
    from unified_calibration_contract import EvidenceAvailability

    analysis = result["analysis"]
    if analysis["validation_errors"]:
        raise ValueError(f"Invalid reference army: {analysis['validation_errors']}")
    army = result["army"]
    if army.total_points() <= 0:
        raise ValueError("Reference army must have positive points")
    snap = extract_mechanical_army_snapshot(
        army_key=army_key, fixture_id=fixture.name,
        source_commit=analysis_commit, analysis=analysis,
        raw_shooting_output_density=normalise_raw_shooting_for_extractor(raw_shooting),
    )
    snap = extend_mechanical_army_snapshot(snap, ProviderEvidenceBundle(
        mobility=analysis.get("mechanical_mobility"),
        magic=analysis.get("mechanical_magic"),
        courage=analysis.get("mechanical_courage"),
    ))
    return {
        "development": "DEV-077S-I2-I-C3-D",
        "source": "fresh_real_army_engine_run",
        "analysis_commit": analysis_commit,
        "roster_file": str(fixture),
        "roster_sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
        "roster_revision": source_revision,
        "army_key": army_key,
        "army_name": result["definition"].name,
        "points_limit": result["definition"].points_limit,
        "points": army.total_points(),
        "models": army.model_count(),
        "raw_shooting_benchmark": "build_shooting_benchmark_defender()",
        "measurements": [asdict(m) for m in snap.measurements],
        "available_count": snap.available_count,
        "partial_count": sum(m.availability is EvidenceAvailability.PARTIAL for m in snap.measurements),
        "unresolved_metrics": list(snap.unresolved_metrics),
        "reference_anchors_approved": False,
        "production_scoring_enabled": False,
        "scenario_scoring_changed": False,
    }


def run(fixture, output, army_key):
    fixture, output = validate_paths(fixture, output)
    from loader import load_all_profiles
    from army_loader import load_factions, load_army_lists
    from profile_option_loader import load_profile_options, build_profile_options_by_external_id
    from profile_option_wargear_loader import load_profile_option_wargear_assignments
    from profile_option_mount_loader import load_profile_option_mount_assignments
    from profile_option_platform_loader import load_profile_option_platform_assignments
    from profile_option_state_effect_loader import load_profile_option_state_effects
    from wargear_loader import load_wargear
    from mount_loader import load_mounts
    from model_platform_loader import load_platforms
    from analysis_loader import load_metric_thresholds
    from rule_loader import (load_special_rules, load_heroic_actions, load_spells,
                             load_ability_tags, load_ability_prerequisites)
    from relationship_loader import (
        load_profile_special_rules, load_profile_heroic_actions, load_profile_spells,
        load_special_rule_tags, load_heroic_action_tags, load_spell_tags,
        load_heroic_action_prerequisites, load_special_rule_prerequisites,
        load_spell_prerequisites,
    )
    from services.mesbg_list_analysis_service import analyse_mesbg_list_builder_file
    from army_shooting_capability import calculate_army_shooting_output_density
    from projection_capability import build_shooting_benchmark_defender

    profiles = {p.id: p for p in load_all_profiles()}
    special_rules = load_special_rules()
    heroic_actions = load_heroic_actions()
    spells = load_spells()
    tags = load_ability_tags()
    prereqs = load_ability_prerequisites()
    load_profile_special_rules(profiles, special_rules)
    load_profile_heroic_actions(profiles, heroic_actions)
    load_profile_spells(profiles, spells)
    load_special_rule_tags(special_rules, tags)
    load_heroic_action_tags(heroic_actions, tags)
    load_spell_tags(spells, tags)
    load_heroic_action_prerequisites(heroic_actions, prereqs)
    load_special_rule_prerequisites(special_rules, prereqs)
    load_spell_prerequisites(spells, prereqs)
    options = load_profile_options(profiles=profiles)
    load_profile_option_wargear_assignments(options, load_wargear())
    load_profile_option_mount_assignments(options, load_mounts())
    load_profile_option_platform_assignments(options, load_platforms())
    load_profile_option_state_effects(options)
    result = analyse_mesbg_list_builder_file(
        str(fixture), profiles_by_id=profiles,
        army_lists_by_id=load_army_lists(load_factions()),
        metric_thresholds=load_metric_thresholds(),
        profile_options_by_external_id=build_profile_options_by_external_id(options),
    )
    raw_shooting = calculate_army_shooting_output_density(
        army=result["army"], defender=build_shooting_benchmark_defender()
    )
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                     cwd=ROOT, text=True).strip()
    document = build_evidence_document(
        fixture=fixture, army_key=army_key, result=result,
        analysis_commit=commit, raw_shooting=raw_shooting,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return document


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--army-key", required=True)
    args = parser.parse_args(argv)
    document = run(args.fixture, args.output, args.army_key)
    print(f"Real-army evidence: {document['army_name']}, {document['points']} pts")
    print(f"Available: {document['available_count']}; partial: {document['partial_count']}")
    print("Unresolved:", ", ".join(document["unresolved_metrics"]))
    print("No scoring changes; candidate anchors not approved.")


if __name__ == "__main__":
    main()

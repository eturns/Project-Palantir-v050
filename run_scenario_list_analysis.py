from army import Army
from army_list import ArmyList
from combat_benchmark import CombatBenchmark
from faction import Faction
from loader import load_all_profiles
from rule_loader import (
    load_special_rules,
    load_heroic_actions,
    load_spells,
    load_ability_tags,
    load_ability_prerequisites,
)

from relationship_loader import (
    load_profile_special_rules,
    load_profile_heroic_actions,
    load_profile_spells,
    load_heroic_action_tags,
    load_special_rule_tags,
    load_spell_tags,
    load_heroic_action_prerequisites,
    load_special_rule_prerequisites,
    load_spell_prerequisites,
)
from optimiser_candidate import OptimiserCandidate
from scenario_analysis_builder import (
    build_scenario_analysis_results_from_candidate,
)
from scenario_analysis_report import (
    build_scenario_analysis_report,
)
from army_rule import ArmyRule


profiles = load_all_profiles()

profiles_by_id = {
    profile.id: profile
    for profile in profiles
}

special_rules = load_special_rules()
heroic_actions = load_heroic_actions()
spells = load_spells()
ability_tags = load_ability_tags()
ability_prerequisites = load_ability_prerequisites()


load_profile_special_rules(
    profiles_by_id,
    special_rules,
)

load_profile_heroic_actions(
    profiles_by_id,
    heroic_actions,
)

load_profile_spells(
    profiles_by_id,
    spells,
)

load_special_rule_tags(
    special_rules,
    ability_tags,
)

load_heroic_action_tags(
    heroic_actions,
    ability_tags,
)

load_spell_tags(
    spells,
    ability_tags,
)

load_heroic_action_prerequisites(
    heroic_actions,
    ability_prerequisites,
)

load_spell_prerequisites(
    spells,
    ability_prerequisites,
)

load_special_rule_prerequisites(
    special_rules,
    ability_prerequisites,
)

army = Army()

army.add_profile(
    profiles_by_id["DG_NEC"],
    quantity=1,
)

army.add_profile(
    profiles_by_id["DG_WK"],
    quantity=1,
)

army.add_profile(
    profiles_by_id["DG_KHM"],
    quantity=1,
)

army.add_profile(
    profiles_by_id["DG_DH"],
    quantity=1,
)

army.add_profile(
    profiles_by_id["DG_FS"],
    quantity=1,
)

army.add_profile(
    profiles_by_id["DG_LS"],
    quantity=1,
)

army.add_profile(
    profiles_by_id["DG_MGS"],
    quantity=2,
)

army.add_profile(
    profiles_by_id["DG_MHS"],
    quantity=3,
)


faction = Faction(
    id="DOL_GULDUR",
    name="Dol Guldur",
)


army_list = ArmyList(
    id="DG_ROTN",
    name="Rise of the Necromancer",
    faction=faction,
    profiles=[
        profile
        for profile in profiles
        if profile.id.startswith("DG_")
    ],
    army_rules=[
        ArmyRule(
            id="DG_POWER_OF_THE_NECROMANCER",
            name="Power of the Necromancer",
        ),
        ArmyRule(
            id="DG_HIS_SPIRIT",
            name="His spirit has lost none of its potency",
        ),
    ],
)


candidate = OptimiserCandidate(
    army=army,
)


key_profile = profiles_by_id["DG_NEC"]


combat_benchmark = CombatBenchmark(
    fight=4,
    strength=4,
    defence=6,
    attacks=1,
    wounds=1,
)


results = build_scenario_analysis_results_from_candidate(
    candidate=candidate,
    army_list=army_list,
    key_profile=key_profile,
    leader_profile=key_profile,
    combat_benchmark=combat_benchmark,
    benchmark_presence=10.0,
    benchmark_manoeuvrability=6.0,
    benchmark_combat_capability=0.5,
    benchmark_fate=3.0,
)

print()
print("========== ALL SCENARIOS ==========")

for result in sorted(
    results,
    key=lambda item: item.score,
    reverse=True,
):
    print(
        f"{result.scenario_name} "
        f"({result.pool.value}) - "
        f"{result.score:.3f}"
    )

    for demand in result.demands:
        print(
            f"  {demand.dimension.value}: "
            f"{demand.capability:.3f}"
        )


report = build_scenario_analysis_report(
    results,
)


print()
print("========================================")
print("PROJECT PALANTIR - SCENARIO ANALYSIS")
print("========================================")
print()
print("Army:")
print("  Sauron the Necromancer x1")
print("  Witch-king x1")
print("  Khamul x1")
print("  Dark Headsman x1")
print("  Forsaken x1")
print("  Lingering Shadow x1")
print("  Mirkwood Giant Spider x2")
print("  Mirkwood Hunting Spider x3")
print()
print(report)
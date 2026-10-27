"""DEV-077-TT-E2: REAL ArmyBuilder and analysis-service audit.

This tests real JSON parsing, ArmyBuilder, Army/FieldedModel points, and
Three Trolls analysis-service wiring. Metric engines are stubbed only in the
service boundary test so score/diagnostic separation can be asserted clearly.
"""
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from army_builder import build_army_from_definition
from profiles import Profile
from importers.mesbg_list_builder_json_importer import build_army_definition_from_data
from three_trolls_upgrades import THREE_TROLLS_UPGRADE_NAMES
from three_trolls_d4e_analysis import build_three_trolls_upgrade_analysis

FIXTURE = Path(__file__).parent / "fixtures" / "the_three_trolls_all_options.json"
IDS = ("TT_BILL", "TT_BERT", "TT_TOM")
COSTS = {"TT_BILL": 150, "TT_BERT": 130, "TT_TOM": 120}


def _profile(pid):
    return Profile(
        id=pid, name=pid, points=COSTS[pid], movement=6,
        fight=6, shooting="5+", strength=6, defence=6,
        attacks=3, wounds=3, courage="4+", intelligence="6+",
        might=1, will=1, fate=1, max_in_army=1,
    )


PROFILES = {pid: _profile(pid) for pid in IDS}
ARMY_LIST = SimpleNamespace(
    id="THREE_TROLLS", name="The Three Trolls",
    warband_composition_rules=(), profile_quantity_relation_rules=(),
    profile_factions_by_id={},
)


def definition_for(upgrades):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["metadata"]["tttSpecialUpgrades"] = list(upgrades)
    return build_army_definition_from_data(data)


def real_army(upgrades):
    definition = definition_for(upgrades)
    army, army_list = build_army_from_definition(
        definition, PROFILES, {"THREE_TROLLS": ARMY_LIST},
    )
    return definition, army, army_list


@pytest.mark.parametrize("amount,total", [(0,400),(1,450),(6,700),(12,1000)])
def test_real_army_builder_points_and_models(amount,total):
    definition, army, army_list = real_army(THREE_TROLLS_UPGRADE_NAMES[:amount])
    assert army_list is ARMY_LIST
    assert army.total_points() == total
    assert army.purchase_points == amount*50
    assert sum(entry.total_points() for entry in army.entries) == 400
    fielded = army.fielded_models()
    assert len(fielded) == 3
    assert {m.profile_id for m in fielded} == set(IDS)
    assert len({m.id for m in fielded}) == 3
    assert all(m.configured_profile is not None for m in fielded)
    assert not army.validate(total)


@pytest.mark.parametrize("amount", [0,1,6,12])
def test_real_army_diagnostic_activations(amount):
    names = THREE_TROLLS_UPGRADE_NAMES[:amount]
    definition, army, _ = real_army(names)
    before = (army.total_points(), army.purchase_points)
    diagnostic = build_three_trolls_upgrade_analysis(definition, army)
    assert diagnostic is not None
    assert len(diagnostic.available_effect_keys) == amount
    assert len(diagnostic.inactive_effect_keys) == 12 - amount
    assert diagnostic.hoard.purchase_points == 50*amount
    assert diagnostic.battlefield_status == "conditional_not_evaluated"
    assert (army.total_points(), army.purchase_points) == before
    assert sum(entry.total_points() for entry in army.entries) == 400


@pytest.mark.parametrize("amount", [0,12])
def test_builder_and_analysis_do_not_mutate_definition(amount):
    definition = definition_for(THREE_TROLLS_UPGRADE_NAMES[:amount])
    saved = copy.deepcopy(definition)
    army, _ = build_army_from_definition(definition, PROFILES, {"THREE_TROLLS": ARMY_LIST})
    build_three_trolls_upgrade_analysis(definition, army)
    assert definition == saved


def test_full_bellies_diagnostic_does_not_mutate_canonical_profile():
    definition, army, _ = real_army(("Full Bellies",))
    diagnostic = build_three_trolls_upgrade_analysis(definition, army)
    assert all((x.starting_might, x.starting_will, x.starting_fate) == (3,3,3)
               for x in diagnostic.starting_resources_by_profile_id.values())
    assert all((p.might,p.will,p.fate)==(1,1,1) for p in PROFILES.values())


def test_cover_and_campfire_purchase_gates_with_real_models():
    zero_def, zero_army, _ = real_army(())
    yes_def, yes_army, _ = real_army(("Cover of Darkness","Nothing like a warm fire"))
    no = build_three_trolls_upgrade_analysis(zero_def,zero_army)
    yes = build_three_trolls_upgrade_analysis(yes_def,yes_army)
    assert no.hoard.campfire_range_inches == 6
    assert yes.hoard.campfire_range_inches == 18
    assert not any(no.cave_dweller_by_profile_id.values())
    assert all(yes.cave_dweller_by_profile_id.values())


def test_real_service_emits_upgrade_diagnostic_without_changing_scores(monkeypatch):
    """Main analysis orchestrator, real army; existing scoring deliberately stubbed."""
    import services.army_analysis_service as service
    import services.mesbg_list_analysis_service as high
    def run(upgrades):
        definition, army, army_list = real_army(upgrades)
        monkeypatch.setattr(high, "import_army_from_mesbg_list_builder",
                            lambda *args, **kwargs: (definition,army,army_list))
        monkeypatch.setattr(high, "get_initial_fielded_model_form_states", lambda **kwargs: ())
        monkeypatch.setattr(high, "build_fielded_model_structures", lambda **kwargs: ())
        monkeypatch.setattr(high, "assess_resurrection_evidence", lambda **kwargs: None)
        monkeypatch.setattr(high, "assess_ranged_wargear_evidence", lambda **kwargs: None)
        monkeypatch.setattr(high, "build_default_scenario_analysis_context",
                            lambda **kwargs: SimpleNamespace(
                              combat_benchmark=None,benchmark_presence=None,
                              benchmark_manoeuvrability=None,benchmark_combat_capability=None,
                              benchmark_fate=None))
        monkeypatch.setattr(high, "analyse_imported_army",
                            lambda *args,**kwargs: {"metric_assessments":{"fixed":42},
                                                      "battlefield_assessments":{"fixed":24}})
        return high.analyse_mesbg_list_builder_file(
            "fixture.json",PROFILES,{"THREE_TROLLS": ARMY_LIST},metric_thresholds={})
    bare = run(())
    bought = run(THREE_TROLLS_UPGRADE_NAMES)
    assert bare["analysis"]["metric_assessments"] == bought["analysis"]["metric_assessments"]
    assert bare["analysis"]["battlefield_assessments"] == bought["analysis"]["battlefield_assessments"]
    assert bare["analysis"]["mechanical_three_trolls_upgrades"].hoard.purchase_points == 0
    assert bought["analysis"]["mechanical_three_trolls_upgrades"].hoard.purchase_points == 600

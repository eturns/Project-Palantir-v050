"""DEV-077S-I2-H1-E: production fixture and shared-resource validation."""
import pytest

from control_army_evidence import ControlCheck, DeclaredControlCast
from control_cross_domain_integration import build_control_cross_domain_evidence
from hero_hunting_resource_adapter import DeclaredMethodSpend, HeroHuntingMethod


FIXTURE = "tests/fixtures/rise_of_the_necromancer_all_options.json"


@pytest.fixture(scope="module")
def real_rise_army():
    from importlib.util import module_from_spec, spec_from_file_location
    from pathlib import Path
    helper_path = Path("tests/test_rise_of_the_necromancer_json_import_integration.py")
    spec = spec_from_file_location("rise_fixture_helpers_h1e", helper_path)
    helper = module_from_spec(spec)
    spec.loader.exec_module(helper)
    load_production_rise_data = helper.load_production_rise_data
    from importers.mesbg_list_builder_json_importer import (
        import_army_definition_from_json,
    )
    from services.mesbg_list_builder_import_service import (
        import_army_from_mesbg_list_builder,
    )
    from relationship_loader import load_profile_spells, load_spell_tags
    from rule_loader import load_spells, load_ability_tags

    profiles, army_lists, options = load_production_rise_data()
    # Explicitly initialise the canonical spell relationships: the general
    # list importer does not guarantee that Magic relationships are loaded.
    spells = load_spells()
    load_spell_tags(spells=spells, ability_tags=load_ability_tags())
    load_profile_spells(profiles=profiles, spells=spells)
    assert import_army_definition_from_json(FIXTURE).leader_profile_id == "DG_NEC"
    _, army, _ = import_army_from_mesbg_list_builder(
        FIXTURE,
        profiles_by_id=profiles,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=options,
    )
    return army


def control_event(event="c1", turn=1, will=1):
    return DeclaredControlCast(
        event_id=event, turn=turn, caster_id="DG_NEC#1",
        target_id="ENEMY#1", spell_id="TRANSFIX", will_spent=will,
        opportunity_legal=ControlCheck.VERIFIED_TRUE,
        target_legal=ControlCheck.VERIFIED_TRUE,
        effect_succeeded=ControlCheck.VERIFIED_TRUE,
    )


def test_real_fixture_import_control_spells(real_rise_army):
    result = build_control_cross_domain_evidence(real_rise_army)
    nec = next(c for c in result.control.casters if c.profile_id == "DG_NEC")
    assert {"TRANSFIX", "COMPEL"}.issubset(nec.control_spell_ids)
    assert result.control.declared_will_spent == 0
    assert result.control.evaluated_casts == ()
    assert result.dashboard_score is None and result.scenario_score is None


def test_real_fixture_declared_cast_is_not_applied_effect(real_rise_army):
    result = build_control_cross_domain_evidence(real_rise_army, (control_event(),))
    assert result.control.evaluated_casts[0].eligible_for_effect_application
    assert result.outcome_status == "no_battlefield_outcomes_inferred"
    nec = next(m for m in result.resources.models if m.model_id == "DG_NEC#1")
    assert nec.remaining.remaining_will == nec.starting.remaining_will - 1


def test_real_fixture_control_and_other_magic_share_will(real_rise_army):
    start = build_control_cross_domain_evidence(real_rise_army)
    nec = next(m for m in start.resources.models if m.model_id == "DG_NEC#1")
    will = nec.starting.remaining_will
    other = (DeclaredMethodSpend(
        model_id="DG_NEC#1", method=HeroHuntingMethod.MAGIC_CAST,
        will=will,
    ),)
    with pytest.raises(ValueError):
        build_control_cross_domain_evidence(real_rise_army, (control_event(),), other)


def test_real_fixture_resource_allocations_do_not_overlap(real_rise_army):
    other = (DeclaredMethodSpend(
        model_id="DG_NEC#1", method=HeroHuntingMethod.MAGIC_RESIST, will=1,
    ),)
    result = build_control_cross_domain_evidence(
        real_rise_army, (control_event(),), other,
    )
    nec = next(m for m in result.resources.models if m.model_id == "DG_NEC#1")
    assert nec.remaining.remaining_will == nec.starting.remaining_will - 2
    assert len(result.resources.declared_spends) == 2


def test_other_spend_unknown_model_rejected(real_rise_army):
    with pytest.raises(ValueError, match="unknown"):
        build_control_cross_domain_evidence(real_rise_army, other_spends=(
            DeclaredMethodSpend(
                model_id="UNFIELDed#1", method=HeroHuntingMethod.MAGIC_CAST,
                will=1,
            ),
        ))


def test_control_does_not_infer_target_or_success(real_rise_army):
    event = DeclaredControlCast(
        event_id="unresolved", turn=1, caster_id="DG_NEC#1",
        target_id="ENEMY#1", spell_id="COMPEL", will_spent=1,
        opportunity_legal=ControlCheck.UNKNOWN,
        target_legal=ControlCheck.UNKNOWN,
        effect_succeeded=ControlCheck.UNKNOWN,
    )
    evidence = build_control_cross_domain_evidence(real_rise_army, (event,))
    assert evidence.control.evaluated_casts[0].result == "unresolved"
    assert not evidence.control.evaluated_casts[0].eligible_for_effect_application


def test_duplicate_control_event_rejected(real_rise_army):
    with pytest.raises(ValueError, match="duplicate"):
        build_control_cross_domain_evidence(
            real_rise_army, (control_event(), control_event()),
        )


def test_reject_non_tuple_other_spends(real_rise_army):
    with pytest.raises(TypeError):
        build_control_cross_domain_evidence(real_rise_army, other_spends=[])

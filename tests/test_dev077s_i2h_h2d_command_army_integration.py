"""H2-D: real imported armies and cross-domain Command budget."""
import pytest
from command_action_declaration import (
    CommandActionDeclaration, CommandCheck, CommandDecision,
)
from command_coverage import CommandCoverageObservation, CommandVerification
from command_army_integration import build_army_command_evidence


@pytest.fixture(scope="module", params=["rise", "hunters"])
def imported_army(request):
    from importers.mesbg_list_builder_json_importer import (
        import_army_definition_from_json,
    )
    from services.mesbg_list_builder_import_service import (
        import_army_from_mesbg_list_builder,
    )
    from relationship_loader import load_profile_heroic_actions
    from rule_loader import load_heroic_actions
    if request.param == "rise":
        from test_rise_of_the_necromancer_json_import_integration import (
            load_production_rise_data,
        )
        fixture = "tests/fixtures/rise_of_the_necromancer_all_options.json"
        profiles, army_lists, options = load_production_rise_data()
        load_profile_heroic_actions(profiles=profiles, heroic_actions=load_heroic_actions())
    else:
        from test_azogs_hunters_json_import_integration import (
            load_production_azogs_hunters_data,
        )
        fixture = "tests/fixtures/azogs_hunters_all_options.json"
        profiles, army_lists, options = load_production_azogs_hunters_data()
    assert import_army_definition_from_json(fixture).leader_profile_id
    _, army, _ = import_army_from_mesbg_list_builder(
        fixture, profiles_by_id=profiles,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=options,
    )
    return army


def declaration(actor, event="move", turn=1):
    return CommandActionDeclaration(
        event_id=event, actor_id=actor.model_id, heroic_action_id="HEROIC_MOVE",
        turn=turn, timing_legal=CommandCheck.VERIFIED_TRUE,
        activation_legal=CommandCheck.VERIFIED_TRUE,
        battlefield_legal=CommandCheck.VERIFIED_TRUE,
    )


def test_real_army_has_heroic_move_and_might(imported_army):
    result = build_army_command_evidence(imported_army)
    assert any("HEROIC_MOVE" in actor.action_ids and actor.starting_might
               for actor in result.actors)
    assert result.dashboard_score is None and result.scenario_score is None


def test_declared_action_spends_real_might(imported_army):
    base = build_army_command_evidence(imported_army)
    actor = next(a for a in base.actors
                 if "HEROIC_MOVE" in a.action_ids and a.starting_might >= 1)
    result = build_army_command_evidence(imported_army, (declaration(actor),))
    assert result.declarations[0].decision is CommandDecision.PERMITTED
    remaining = dict(result.remaining_resources)[actor.model_id]
    assert remaining.remaining_might == actor.starting_might - 1


def test_cross_domain_might_competes_with_command(imported_army):
    base = build_army_command_evidence(imported_army)
    actor = next(a for a in base.actors
                 if "HEROIC_MOVE" in a.action_ids and a.starting_might >= 1)
    result = build_army_command_evidence(
        imported_army, (declaration(actor),),
        other_might_spends=((actor.model_id, actor.starting_might),),
    )
    assert result.declarations[0].decision is CommandDecision.FORBIDDEN


def test_unsupported_coverage_cannot_claim_verified_command(imported_army):
    actors = build_army_command_evidence(imported_army).actors
    actor = next(a for a in actors if "HEROIC_MOVE" in a.action_ids and a.starting_might)
    obs = CommandCoverageObservation(
        command_id="unverified", provider_id=actor.model_id,
        recipient_id=actors[-1].model_id, benefit_id="move", turn=1,
        provider_permission=CommandVerification.VERIFIED_TRUE,
        recipient_eligible=CommandVerification.VERIFIED_TRUE,
        within_required_range=CommandVerification.VERIFIED_TRUE,
        timing_permitted=CommandVerification.VERIFIED_TRUE,
    )
    with pytest.raises(ValueError, match="without permitted command"):
        build_army_command_evidence(imported_army, coverage=(obs,))


def test_duplicate_command_event_rejected(imported_army):
    base = build_army_command_evidence(imported_army)
    actor = next(a for a in base.actors if "HEROIC_MOVE" in a.action_ids and a.starting_might)
    with pytest.raises(ValueError, match="duplicate"):
        build_army_command_evidence(imported_army, (declaration(actor), declaration(actor)))


def test_no_outcome_or_weights_assumed(imported_army):
    report = build_army_command_evidence(imported_army)
    assert report.coverage.distinct_verified_model_turn_benefits == 0
    assert report.evidence_status == "roster_and_explicit_opportunities_only"

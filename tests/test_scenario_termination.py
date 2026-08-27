import pytest

from scenario_definition import TerminationType

from scenario_termination import (
    ScenarioTerminationResult,
    evaluate_broken_random_termination,
    evaluate_quarter_strength_termination,
    evaluate_scenario_definition_termination,
    evaluate_scenario_termination,
    evaluate_seize_the_prizes_termination,
)
from scenario_catalogue import get_official_scenario

def test_scenario_termination_result_stores_ended_state():
    result = ScenarioTerminationResult(
        has_ended=True,
        reason="quarter_strength",
    )

    assert result.has_ended is True
    assert result.reason == "quarter_strength"


def test_scenario_termination_result_stores_not_ended_state():
    result = ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )

    assert result.has_ended is False
    assert result.reason is None


def test_scenario_termination_result_is_immutable():
    result = ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )

    with pytest.raises(AttributeError):
        result.has_ended = True


def test_scenario_termination_result_requires_boolean_has_ended():
    with pytest.raises(
        TypeError,
        match="has_ended must be a bool.",
    ):
        ScenarioTerminationResult(
            has_ended=1,
            reason=None,
        )


def test_ended_result_requires_reason():
    with pytest.raises(
        ValueError,
        match="Ended scenario termination result requires a reason.",
    ):
        ScenarioTerminationResult(
            has_ended=True,
            reason=None,
        )


def test_not_ended_result_rejects_reason():
    with pytest.raises(
        ValueError,
        match="Non-ended scenario termination result cannot have a reason.",
    ):
        ScenarioTerminationResult(
            has_ended=False,
            reason="quarter_strength",
        )

def test_quarter_strength_termination_ends_when_first_army_is_at_quarter_strength():
    result = evaluate_quarter_strength_termination(
        first_army_at_quarter_strength=True,
        second_army_at_quarter_strength=False,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="quarter_strength",
    )


def test_quarter_strength_termination_ends_when_second_army_is_at_quarter_strength():
    result = evaluate_quarter_strength_termination(
        first_army_at_quarter_strength=False,
        second_army_at_quarter_strength=True,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="quarter_strength",
    )


def test_quarter_strength_termination_ends_when_both_armies_are_at_quarter_strength():
    result = evaluate_quarter_strength_termination(
        first_army_at_quarter_strength=True,
        second_army_at_quarter_strength=True,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="quarter_strength",
    )


def test_quarter_strength_termination_continues_when_neither_army_is_at_quarter_strength():
    result = evaluate_quarter_strength_termination(
        first_army_at_quarter_strength=False,
        second_army_at_quarter_strength=False,
    )

    assert result == ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )


def test_quarter_strength_termination_rejects_invalid_first_army_state():
    with pytest.raises(
        TypeError,
        match="first_army_at_quarter_strength must be a bool.",
    ):
        evaluate_quarter_strength_termination(
            first_army_at_quarter_strength=1,
            second_army_at_quarter_strength=False,
        )


def test_quarter_strength_termination_rejects_invalid_second_army_state():
    with pytest.raises(
        TypeError,
        match="second_army_at_quarter_strength must be a bool.",
    ):
        evaluate_quarter_strength_termination(
            first_army_at_quarter_strength=False,
            second_army_at_quarter_strength=1,
        )

def test_broken_random_termination_continues_when_neither_army_is_broken():
    result = evaluate_broken_random_termination(
        first_army_broken=False,
        second_army_broken=False,
        end_roll=None,
    )

    assert result == ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )


def test_broken_random_termination_requires_no_roll_before_broken():
    result = evaluate_broken_random_termination(
        first_army_broken=False,
        second_army_broken=False,
        end_roll=None,
    )

    assert result.has_ended is False


def test_broken_random_termination_ends_on_roll_of_one():
    result = evaluate_broken_random_termination(
        first_army_broken=True,
        second_army_broken=False,
        end_roll=1,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="broken_random",
    )


def test_broken_random_termination_ends_on_roll_of_two():
    result = evaluate_broken_random_termination(
        first_army_broken=False,
        second_army_broken=True,
        end_roll=2,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="broken_random",
    )


def test_broken_random_termination_continues_on_roll_of_three():
    result = evaluate_broken_random_termination(
        first_army_broken=True,
        second_army_broken=False,
        end_roll=3,
    )

    assert result == ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )


def test_broken_random_termination_continues_on_roll_of_six():
    result = evaluate_broken_random_termination(
        first_army_broken=True,
        second_army_broken=True,
        end_roll=6,
    )

    assert result == ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )


def test_broken_random_termination_requires_roll_once_eligible():
    with pytest.raises(
        ValueError,
        match=(
            "end_roll is required when at least one army is Broken."
        ),
    ):
        evaluate_broken_random_termination(
            first_army_broken=True,
            second_army_broken=False,
            end_roll=None,
        )


def test_broken_random_termination_rejects_roll_before_eligible():
    with pytest.raises(
        ValueError,
        match=(
            "end_roll must be None when neither army is Broken."
        ),
    ):
        evaluate_broken_random_termination(
            first_army_broken=False,
            second_army_broken=False,
            end_roll=1,
        )


def test_broken_random_termination_rejects_invalid_first_broken_state():
    with pytest.raises(
        TypeError,
        match="first_army_broken must be a bool.",
    ):
        evaluate_broken_random_termination(
            first_army_broken=1,
            second_army_broken=False,
            end_roll=None,
        )


def test_broken_random_termination_rejects_invalid_second_broken_state():
    with pytest.raises(
        TypeError,
        match="second_army_broken must be a bool.",
    ):
        evaluate_broken_random_termination(
            first_army_broken=False,
            second_army_broken=1,
            end_roll=None,
        )


def test_broken_random_termination_rejects_roll_below_one():
    with pytest.raises(
        ValueError,
        match="end_roll must be between 1 and 6.",
    ):
        evaluate_broken_random_termination(
            first_army_broken=True,
            second_army_broken=False,
            end_roll=0,
        )


def test_broken_random_termination_rejects_roll_above_six():
    with pytest.raises(
        ValueError,
        match="end_roll must be between 1 and 6.",
    ):
        evaluate_broken_random_termination(
            first_army_broken=True,
            second_army_broken=False,
            end_roll=7,
        )


def test_broken_random_termination_rejects_non_integer_roll():
    with pytest.raises(
        TypeError,
        match="end_roll must be an int or None.",
    ):
        evaluate_broken_random_termination(
            first_army_broken=True,
            second_army_broken=False,
            end_roll=2.0,
        )

def test_scenario_termination_dispatches_quarter_strength():
    result = evaluate_scenario_termination(
        termination_type=TerminationType.QUARTER_STRENGTH,
        first_army_at_quarter_strength=True,
        second_army_at_quarter_strength=False,
        first_army_broken=False,
        second_army_broken=False,
        end_roll=None,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="quarter_strength",
    )


def test_scenario_termination_dispatches_broken_random():
    result = evaluate_scenario_termination(
        termination_type=TerminationType.BROKEN_RANDOM,
        first_army_at_quarter_strength=False,
        second_army_at_quarter_strength=False,
        first_army_broken=True,
        second_army_broken=False,
        end_roll=2,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="broken_random",
    )


def test_scenario_termination_broken_random_can_continue():
    result = evaluate_scenario_termination(
        termination_type=TerminationType.BROKEN_RANDOM,
        first_army_at_quarter_strength=False,
        second_army_at_quarter_strength=False,
        first_army_broken=True,
        second_army_broken=False,
        end_roll=5,
    )

    assert result == ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )


def test_scenario_termination_rejects_scenario_specific_without_handler():
    with pytest.raises(
        NotImplementedError,
        match=(
            "Scenario-specific termination requires a dedicated handler."
        ),
    ):
        evaluate_scenario_termination(
            termination_type=TerminationType.SCENARIO_SPECIFIC,
            first_army_at_quarter_strength=False,
            second_army_at_quarter_strength=False,
            first_army_broken=False,
            second_army_broken=False,
            end_roll=None,
        )


def test_scenario_termination_rejects_invalid_termination_type():
    with pytest.raises(
        TypeError,
        match="termination_type must be a TerminationType.",
    ):
        evaluate_scenario_termination(
            termination_type="quarter_strength",
            first_army_at_quarter_strength=False,
            second_army_at_quarter_strength=False,
            first_army_broken=False,
            second_army_broken=False,
            end_roll=None,
        )


def test_quarter_strength_dispatch_ignores_broken_state_and_end_roll():
    result = evaluate_scenario_termination(
        termination_type=TerminationType.QUARTER_STRENGTH,
        first_army_at_quarter_strength=False,
        second_army_at_quarter_strength=False,
        first_army_broken=True,
        second_army_broken=True,
        end_roll=1,
    )

    assert result == ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )

def test_seize_the_prizes_ends_when_all_artefacts_are_removed():
    result = evaluate_seize_the_prizes_termination(
        artefacts_removed=3,
        first_army_at_quarter_strength=False,
        second_army_at_quarter_strength=False,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="all_artefacts_removed",
    )


def test_seize_the_prizes_ends_when_both_armies_are_at_quarter_strength():
    result = evaluate_seize_the_prizes_termination(
        artefacts_removed=0,
        first_army_at_quarter_strength=True,
        second_army_at_quarter_strength=True,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="both_armies_at_quarter_strength",
    )


def test_seize_the_prizes_continues_when_only_one_army_is_at_quarter_strength():
    result = evaluate_seize_the_prizes_termination(
        artefacts_removed=0,
        first_army_at_quarter_strength=True,
        second_army_at_quarter_strength=False,
    )

    assert result == ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )


def test_seize_the_prizes_continues_with_fewer_than_three_artefacts_removed():
    result = evaluate_seize_the_prizes_termination(
        artefacts_removed=2,
        first_army_at_quarter_strength=False,
        second_army_at_quarter_strength=False,
    )

    assert result == ScenarioTerminationResult(
        has_ended=False,
        reason=None,
    )


def test_seize_the_prizes_artefact_removal_takes_precedence_when_both_conditions_met():
    result = evaluate_seize_the_prizes_termination(
        artefacts_removed=3,
        first_army_at_quarter_strength=True,
        second_army_at_quarter_strength=True,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="all_artefacts_removed",
    )


def test_seize_the_prizes_rejects_negative_artefact_count():
    with pytest.raises(
        ValueError,
        match="artefacts_removed must be between 0 and 3.",
    ):
        evaluate_seize_the_prizes_termination(
            artefacts_removed=-1,
            first_army_at_quarter_strength=False,
            second_army_at_quarter_strength=False,
        )


def test_seize_the_prizes_rejects_artefact_count_above_three():
    with pytest.raises(
        ValueError,
        match="artefacts_removed must be between 0 and 3.",
    ):
        evaluate_seize_the_prizes_termination(
            artefacts_removed=4,
            first_army_at_quarter_strength=False,
            second_army_at_quarter_strength=False,
        )


def test_seize_the_prizes_rejects_non_integer_artefact_count():
    with pytest.raises(
        TypeError,
        match="artefacts_removed must be an int.",
    ):
        evaluate_seize_the_prizes_termination(
            artefacts_removed=2.0,
            first_army_at_quarter_strength=False,
            second_army_at_quarter_strength=False,
        )


def test_seize_the_prizes_rejects_invalid_first_army_state():
    with pytest.raises(
        TypeError,
        match="first_army_at_quarter_strength must be a bool.",
    ):
        evaluate_seize_the_prizes_termination(
            artefacts_removed=0,
            first_army_at_quarter_strength=1,
            second_army_at_quarter_strength=False,
        )


def test_seize_the_prizes_rejects_invalid_second_army_state():
    with pytest.raises(
        TypeError,
        match="second_army_at_quarter_strength must be a bool.",
    ):
        evaluate_seize_the_prizes_termination(
            artefacts_removed=0,
            first_army_at_quarter_strength=False,
            second_army_at_quarter_strength=1,
        )

def test_scenario_termination_dispatches_seize_the_prizes():
    result = evaluate_scenario_termination(
        termination_type=TerminationType.SCENARIO_SPECIFIC,
        scenario_id="SEIZE_THE_PRIZES",
        first_army_at_quarter_strength=False,
        second_army_at_quarter_strength=False,
        first_army_broken=False,
        second_army_broken=False,
        end_roll=None,
        artefacts_removed=3,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="all_artefacts_removed",
    )


def test_scenario_termination_dispatches_seize_the_prizes_quarter_strength_condition():
    result = evaluate_scenario_termination(
        termination_type=TerminationType.SCENARIO_SPECIFIC,
        scenario_id="SEIZE_THE_PRIZES",
        first_army_at_quarter_strength=True,
        second_army_at_quarter_strength=True,
        first_army_broken=False,
        second_army_broken=False,
        end_roll=None,
        artefacts_removed=0,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="both_armies_at_quarter_strength",
    )


def test_scenario_specific_termination_requires_scenario_id():
    with pytest.raises(
        ValueError,
        match=(
            "scenario_id is required for scenario-specific termination."
        ),
    ):
        evaluate_scenario_termination(
            termination_type=TerminationType.SCENARIO_SPECIFIC,
            scenario_id=None,
            first_army_at_quarter_strength=False,
            second_army_at_quarter_strength=False,
            first_army_broken=False,
            second_army_broken=False,
            end_roll=None,
            artefacts_removed=0,
        )


def test_scenario_specific_termination_rejects_unknown_scenario_id():
    with pytest.raises(
        NotImplementedError,
        match=(
            "No scenario-specific termination handler for: UNKNOWN_SCENARIO"
        ),
    ):
        evaluate_scenario_termination(
            termination_type=TerminationType.SCENARIO_SPECIFIC,
            scenario_id="UNKNOWN_SCENARIO",
            first_army_at_quarter_strength=False,
            second_army_at_quarter_strength=False,
            first_army_broken=False,
            second_army_broken=False,
            end_roll=None,
            artefacts_removed=0,
        )

def test_scenario_definition_termination_dispatches_quarter_strength_scenario():
    scenario = get_official_scenario("DOMINATION")

    result = evaluate_scenario_definition_termination(
        scenario=scenario,
        first_army_at_quarter_strength=True,
        second_army_at_quarter_strength=False,
        first_army_broken=False,
        second_army_broken=False,
        end_roll=None,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="quarter_strength",
    )


def test_scenario_definition_termination_dispatches_broken_random_scenario():
    scenario = get_official_scenario("HOLD_GROUND")

    result = evaluate_scenario_definition_termination(
        scenario=scenario,
        first_army_at_quarter_strength=False,
        second_army_at_quarter_strength=False,
        first_army_broken=True,
        second_army_broken=False,
        end_roll=2,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="broken_random",
    )


def test_scenario_definition_termination_dispatches_seize_the_prizes():
    scenario = get_official_scenario("SEIZE_THE_PRIZES")

    result = evaluate_scenario_definition_termination(
        scenario=scenario,
        first_army_at_quarter_strength=False,
        second_army_at_quarter_strength=False,
        first_army_broken=False,
        second_army_broken=False,
        end_roll=None,
        artefacts_removed=3,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="all_artefacts_removed",
    )


def test_scenario_definition_termination_uses_scenario_identity_automatically():
    scenario = get_official_scenario("SEIZE_THE_PRIZES")

    result = evaluate_scenario_definition_termination(
        scenario=scenario,
        first_army_at_quarter_strength=True,
        second_army_at_quarter_strength=True,
        first_army_broken=False,
        second_army_broken=False,
        end_roll=None,
        artefacts_removed=0,
    )

    assert result == ScenarioTerminationResult(
        has_ended=True,
        reason="both_armies_at_quarter_strength",
    )


def test_scenario_definition_termination_rejects_invalid_scenario():
    with pytest.raises(
        TypeError,
        match="scenario must be a ScenarioDefinition.",
    ):
        evaluate_scenario_definition_termination(
            scenario="DOMINATION",
            first_army_at_quarter_strength=False,
            second_army_at_quarter_strength=False,
            first_army_broken=False,
            second_army_broken=False,
            end_roll=None,
        )
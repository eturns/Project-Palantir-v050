"""
Project Palantír
DEV-080-F2: Real-army casting output acceptance.

Author: Edward Turns (Project Lead)

Tests the Necromancer's six-activation casting
output envelope using actual army-level evidence.
"""

import pytest

from main import run_analysis_workflow
from army_magic_capability_assessment import (
    assess_army_magic_capability,
)
from magic_casting_output_envelope import (
    calculate_casting_output_envelope,
)


@pytest.fixture(scope="module")
def necromancer_evidence():
    imported = run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )

    assessment = assess_army_magic_capability(
        imported["army"],
        imported["army_list"],
    )

    effectiveness = assessment.caster_effectiveness[0][1]
    capacity = assessment.caster_capacity[0][1]

    return effectiveness, capacity


def test_necromancer_real_casting_output(necromancer_evidence):
    effectiveness, capacity = necromancer_evidence

    probabilities = tuple(
        (spell_id, enhanced)
        for spell_id, baseline, enhanced
        in effectiveness.spell_results
    )

    result = calculate_casting_output_envelope(
        spell_probabilities=probabilities,
        starting_will=capacity.starting_will,
        hypothetical_activations=(
            capacity.hypothetical_activations
        ),
        permitted_attempts_per_activation=(
            capacity.permitted_attempts_per_activation
        ),
    )

    assert result.modelled_attempts == 12

    # Two different 3+ spells can be selected
    # in each of the six hypothetical activations.
    assert result.maximum_expected_successes == pytest.approx(
        32 / 3
    )

    # Two different 5+ spells provide the
    # lower fixed-attempt casting envelope.
    assert result.minimum_expected_successes == pytest.approx(
        20 / 3
    )

    assert result.dashboard_score is None
    assert result.scenario_score is None
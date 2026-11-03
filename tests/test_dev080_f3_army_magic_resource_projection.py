"""
Project Palantír
DEV-080-F3: Real-Army Magic Resource Acceptance.

Author: Edward Turns (Project Lead)

Checks resource projections against actual imported
Necromancer and Smaug army fixtures.

No production scoring or calibration changes.
"""

import pytest

from main import run_analysis_workflow
from army_magic_capability_assessment import (
    assess_army_magic_capability,
)
from army_magic_resource_projection import (
    assess_army_magic_resources,
)
from army_magic_output_envelope import (
    assess_army_magic_output,
)


@pytest.fixture(scope="module")
def real_army_results():
    results = {}

    for name, fixture in (
        ("necromancer", "dol_guldur_700.json"),
        ("smaug", "smaug.json"),
        ("non_magic", "azogs-hunters.json"),
    ):
        imported = run_analysis_workflow(
            f"tests/fixtures/{fixture}",
            print_report=False,
        )

        army = imported["army"]

        magic = assess_army_magic_capability(
            army,
            imported["army_list"],
        )

        resources = assess_army_magic_resources(
            army,
            magic,
        )

        output = assess_army_magic_output(magic)

        results[name] = (magic, resources, output)

    return results


def test_necromancer_permanent_will_projection(
    real_army_results,
):
    _, resources, output = real_army_results["necromancer"]

    assert resources.funded_attempts == 12
    assert resources.temporary_will_spent == 0
    assert resources.permanent_will_spent == 12
    assert resources.permanent_will_remaining == 13

    assert output.modelled_attempts == 12


def test_smaug_temporary_will_projection(
    real_army_results,
):
    _, resources, output = real_army_results["smaug"]

    assert resources.funded_attempts == 6
    assert resources.temporary_will_spent == 6
    assert resources.permanent_will_spent == 0
    assert resources.permanent_will_remaining == 6

    assert output.modelled_attempts == 6


def test_smaug_individual_turns(
    real_army_results,
):
    _, resources, _ = real_army_results["smaug"]

    assert len(resources.caster_results) == 1

    _, projection = resources.caster_results[0]

    assert len(projection.turns) == 6

    for turn in projection.turns:
        assert turn.requested_attempts == 1
        assert turn.funded_attempts == 1
        assert turn.temporary_will_spent == 1
        assert turn.permanent_will_spent == 0
        assert turn.permanent_will_remaining == 6


def test_non_magic_army_has_no_casting_resources(
    real_army_results,
):
    _, resources, output = real_army_results["non_magic"]

    assert resources.caster_results == ()
    assert resources.funded_attempts == 0
    assert resources.temporary_will_spent == 0
    assert resources.permanent_will_spent == 0
    assert resources.permanent_will_remaining == 0
    assert output.modelled_attempts == 0


def test_resource_projection_is_diagnostic_only(
    real_army_results,
):
    for _, resources, _ in real_army_results.values():
        assert resources.dashboard_score is None
        assert resources.scenario_score is None
        assert resources.evidence_status == (
            "conditional_army_resource_projection"
        )
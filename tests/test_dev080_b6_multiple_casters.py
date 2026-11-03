
"""
Project Palantír
DEV-080-B6: Multiple-caster Magic acceptance.

Author: Edward Turns (Project Lead)

Synthetic quantity test using a real imported
Necromancer profile. Diagnostic only.
"""

import pytest

from army import Army
from main import run_analysis_workflow
from army_magic_capability_assessment import (
    assess_army_magic_capability,
)


@pytest.fixture(scope="module")
def duplicated_casters():
    imported = run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )

    source_army = imported["army"]
    army_list = imported["army_list"]

    necromancer = next(
        model for model in source_army.fielded_models()
        if model.profile_id == "DG_NEC"
    )

    army = Army()
    army.add_configured_profile(
        necromancer.configured_profile,
        quantity=2,
    )

    return assess_army_magic_capability(
        army, army_list
    )


def test_two_casters_preserved(duplicated_casters):
    result = duplicated_casters

    assert result.caster_count == 2
    assert len(result.caster_effectiveness) == 2


def test_caster_ids_remain_distinct(duplicated_casters):
    ids = [
        model_id
        for model_id, _ in
        duplicated_casters.caster_effectiveness
    ]

    assert len(set(ids)) == 2


def test_resources_are_quantity_weighted(duplicated_casters):
    result = duplicated_casters

    assert result.starting_caster_will == 50
    assert result.one_will_attempt_ceiling == 50


def test_each_caster_has_independent_evidence(duplicated_casters):
    assessments = [
        assessment
        for _, assessment in
        duplicated_casters.caster_effectiveness
    ]

    assert all(
        item.spell_count == 9
        for item in assessments
    )

    assert all(
        item.enhanced_probability == pytest.approx(61 / 81)
        for item in assessments
    )


def test_no_premature_composite_score(duplicated_casters):
    result = duplicated_casters

    assert result.dashboard_score is None
    assert result.scenario_score is None

def test_zero_effective_will_prevents_funded_casting():
    """
    A starting-resource override must take precedence
    over the base profile's Will characteristic.
    """
    imported = run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )

    necromancer = next(
        model for model in imported["army"].fielded_models()
        if model.profile_id == "DG_NEC"
    )

    army = Army()
    army.add_configured_profile(
        necromancer.configured_profile
    )

    army.entries[0].starting_resource_overrides = {
        "will": 0
    }

    assert army.entries[0].get_attribute("will") == 0

    result = assess_army_magic_capability(
        army,
        imported["army_list"],
    )

    assert result.starting_caster_will == 0
    assert result.caster_effectiveness == ()

def test_positive_will_override_limits_casting_resources():
    """Effective starting Will must govern casting allocations."""
    imported = run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )

    necromancer = next(
        model for model in imported["army"].fielded_models()
        if model.profile_id == "DG_NEC"
    )

    army = Army()
    army.add_configured_profile(
        necromancer.configured_profile
    )

    army.entries[0].starting_resource_overrides = {
        "will": 2
    }

    result = assess_army_magic_capability(
        army,
        imported["army_list"],
    )

    assert result.starting_caster_will == 2
    assert result.one_will_attempt_ceiling == 2
    assert len(result.caster_effectiveness) == 1

    _, effectiveness = result.caster_effectiveness[0]

    assert effectiveness.spell_count == 9
    assert effectiveness.baseline_probability == pytest.approx(
        14 / 27
    )
    assert effectiveness.enhanced_probability == pytest.approx(
        61 / 81
    )

    # Casting success per one-Will attempt remains
    # unchanged, even though endurance is reduced.
    assert effectiveness.extra_casting_dice == 1
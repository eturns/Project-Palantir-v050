
"""
Project Palantír
DEV-080-B3: Real-army Magic measurement acceptance.

Author: Edward Turns (Project Lead)
"""

import pytest

from main import run_analysis_workflow
from mechanical_magic_spell_profiles import (
    build_profile_magic_casting_evidence,
)
from magic_capability_measurement import (
    measure_magic_casting_potential,
)


@pytest.fixture(scope="module")
def real_necromancer():
    result = run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )

    assert result is not None

    army = result["army"]
    army_list = result["army_list"]

    necromancer = next(
        model
        for model in army.fielded_models()
        if model.profile_id == "DG_NEC"
    )

    evidence = build_profile_magic_casting_evidence(
        necromancer.configured_profile,
        army=army,
        army_list=army_list,
    )

    active_rules = tuple(
        rule.id for rule in army_list.army_rules
    )

    return evidence, active_rules


def test_real_necromancer_normal_cast(real_necromancer):
    evidence, _ = real_necromancer

    result = measure_magic_casting_potential(
        evidence,
        spell_id="TRANSFIX",
    )

    assert result.casting_probability == pytest.approx(2 / 3)
    assert result.additional_dice == 0


def test_real_necromancer_bonus_cast(real_necromancer):
    evidence, active_rules = real_necromancer

    assert "DG_HIS_SPIRIT" in active_rules

    result = measure_magic_casting_potential(
        evidence,
        spell_id="TRANSFIX",
        verified_rule_ids=("DG_HIS_SPIRIT",),
    )

    assert result.casting_probability == pytest.approx(8 / 9)
    assert result.additional_dice == 1
    assert result.will_spent == 1
    assert result.remaining_will == evidence.will_available - 1


def test_real_magic_remains_diagnostic(real_necromancer):
    evidence, active_rules = real_necromancer

    result = measure_magic_casting_potential(
        evidence,
        spell_id="TRANSFIX",
        verified_rule_ids=("DG_HIS_SPIRIT",),
    )

    assert result.dashboard_score is None
    assert result.scenario_score is None
    assert result.evidence_status == "diagnostic_not_calibrated"
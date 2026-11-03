
"""
Project Palantír
DEV-080-B2: Magic capability measurement tests.

Author: Edward Turns (Project Lead)
"""

import pytest

from magic_capability_measurement import (
    measure_magic_casting_potential,
)
from mechanical_magic_casting import calculate_cast_evidence
from mechanical_magic_spell_profiles import (
    ProfileMagicCastingEvidence,
    SpellCastingOptions,
)


def make_evidence(*, will=3, include_bonus=True):
    """Build controlled Necromancer casting evidence."""

    normal = SpellCastingOptions(
        spell_id="TRANSFIX",
        spell_name="Transfix",
        cast_value=4,
        allocations=(
            calculate_cast_evidence(
                cast_value=4,
                will_available=will,
                will_spent=1,
            ),
        ) if will >= 1 else (),
        conditional_rule_ids=(),
    )

    options = [normal]

    if include_bonus:
        bonus = SpellCastingOptions(
            spell_id="TRANSFIX",
            spell_name="Transfix",
            cast_value=4,
            allocations=(
                calculate_cast_evidence(
                    cast_value=4,
                    will_available=will,
                    will_spent=1,
                    additional_dice=1,
                    extra_dice_source="DG_HIS_SPIRIT",
                ),
            ) if will >= 1 else (),
            conditional_rule_ids=("DG_HIS_SPIRIT",),
        )
        options.append(bonus)

    return ProfileMagicCastingEvidence(
        profile_id="DG_NEC",
        will_available=will,
        spell_options=tuple(options),
        excluded_spell_ids=(),
        conditional_extra_casting_dice=(
            1 if include_bonus else 0
        ),
        conditional_extra_casting_dice_sources=(
            ("DG_HIS_SPIRIT",) if include_bonus else ()
        ),
        conditional_extra_casts_per_opportunity=0,
        conditional_extra_cast_sources=(),
    )


def test_normal_casting_probability():
    result = measure_magic_casting_potential(
        make_evidence(),
        spell_id="TRANSFIX",
    )

    assert result.casting_probability == pytest.approx(0.5)
    assert result.additional_dice == 0
    assert result.remaining_will == 2


def test_necromancer_bonus_die():
    result = measure_magic_casting_potential(
        make_evidence(),
        spell_id="TRANSFIX",
        verified_rule_ids=("DG_HIS_SPIRIT",),
    )

    assert result.casting_probability == pytest.approx(0.75)
    assert result.additional_dice == 1
    assert result.will_spent == 1
    assert result.remaining_will == 2


def test_bonus_requires_verified_rule():
    result = measure_magic_casting_potential(
        make_evidence(),
        spell_id="TRANSFIX",
        verified_rule_ids=(),
    )

    assert result.additional_dice == 0
    assert result.casting_probability == pytest.approx(0.5)


def test_zero_will_cannot_fund_cast():
    with pytest.raises(ValueError, match="Will allocation"):
        measure_magic_casting_potential(
            make_evidence(will=0),
            spell_id="TRANSFIX",
        )


def test_unknown_spell_rejected():
    with pytest.raises(ValueError, match="unavailable"):
        measure_magic_casting_potential(
            make_evidence(),
            spell_id="UNKNOWN_SPELL",
        )


def test_measurement_remains_diagnostic():
    result = measure_magic_casting_potential(
        make_evidence(),
        spell_id="TRANSFIX",
    )

    assert result.dashboard_score is None
    assert result.scenario_score is None
    assert result.evidence_status == "diagnostic_not_calibrated"
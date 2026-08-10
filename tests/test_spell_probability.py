import pytest
from database.rule_category import RuleCategory
from profile_spell_assignment import ProfileSpellAssignment
from spell import Spell

from spell_probability import (
    casting_probability,
    casting_probability_for_spell_assignment,
    casting_probability_with_resource_state,
    heroic_channelling_cast_probability,
    heroic_channelling_cast_result,
)
from hero_resource_state import HeroResourceState

def test_casting_probability_on_one_die():
    assert casting_probability(
        cast_value=3,
    ) == pytest.approx(
        2 / 3
    )


def test_casting_probability_improves_with_two_dice():
    assert casting_probability(
        cast_value=3,
        dice_count=2,
    ) == pytest.approx(
        8 / 9
    )


def test_casting_probability_improves_with_three_dice():
    assert casting_probability(
        cast_value=3,
        dice_count=3,
    ) == pytest.approx(
        26 / 27
    )


def test_casting_probability_is_zero_with_zero_dice():
    assert casting_probability(
        cast_value=3,
        dice_count=0,
    ) == 0

def test_casting_probability_uses_available_will():
    resources = HeroResourceState(
        remaining_will=2,
    )

    assert casting_probability_with_resource_state(
        cast_value=3,
        resources=resources,
        will_points_to_spend=2,
    ) == pytest.approx(
        8 / 9
    )


def test_casting_rejects_more_will_than_remains():
    resources = HeroResourceState(
        remaining_will=1,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Cannot spend more Will than the "
            "caster has remaining."
        ),
    ):
        casting_probability_with_resource_state(
            cast_value=3,
            resources=resources,
            will_points_to_spend=2,
        )


def test_casting_requires_at_least_one_will():
    resources = HeroResourceState(
        remaining_will=2,
    )

    with pytest.raises(
        ValueError,
        match="At least one Will Point must be spent to cast.",
    ):
        casting_probability_with_resource_state(
            cast_value=3,
            resources=resources,
            will_points_to_spend=0,
        )

def test_casting_probability_uses_stored_spell_assignment_cast_value():
    spell_assignment = ProfileSpellAssignment(
        spell=Spell(
            id="TRANSFIX",
            name="Transfix",
            category=RuleCategory.COMMAND,
        ),
        cast_value=3,
    )

    assert casting_probability_for_spell_assignment(
        spell_assignment=spell_assignment,
        dice_count=2,
    ) == pytest.approx(
        8 / 9
    )

def test_heroic_channelling_cast_is_automatic():
    resources = HeroResourceState(
        remaining_will=1,
    )

    assert heroic_channelling_cast_probability(
        resources=resources,
    ) == 1.0


def test_heroic_channelling_requires_will():
    resources = HeroResourceState(
        remaining_will=0,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Heroic Channelling still requires "
            "one Will Point to cast."
        ),
    ):
        heroic_channelling_cast_probability(
            resources=resources,
        )

def test_heroic_channelling_cast_result_is_six():
    resources = HeroResourceState(
        remaining_will=1,
    )

    assert heroic_channelling_cast_result(
        resources=resources,
    ) == 6
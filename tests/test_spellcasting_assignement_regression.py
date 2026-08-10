import pytest

from database.rule_category import RuleCategory
from hero_resource_state import HeroResourceState
from profile_spell_assignment import ProfileSpellAssignment
from resistance_probability import resistance_probability
from spell import Spell
from spell_probability import (
    casting_probability_for_spell_assignment,
    heroic_channelling_cast_probability,
    heroic_channelling_cast_result,
)


def test_spellcasting_assignment_regression():
    spell_assignment = ProfileSpellAssignment(
        spell=Spell(
            id="TRANSFIX",
            name="Transfix",
            category=RuleCategory.COMMAND,
        ),
        cast_value=3,
    )

    caster_resources = HeroResourceState(
        remaining_will=2,
    )

    normal_cast_probability = (
        casting_probability_for_spell_assignment(
            spell_assignment=spell_assignment,
            dice_count=1,
        )
    )

    channelled_cast_probability = (
        heroic_channelling_cast_probability(
            resources=caster_resources,
        )
    )

    channelled_cast_result = (
        heroic_channelling_cast_result(
            resources=caster_resources,
        )
    )

    resist_probability = resistance_probability(
        casting_highest_roll=channelled_cast_result,
        dice_count=1,
    )

    assert normal_cast_probability == pytest.approx(
        2 / 3
    )

    assert channelled_cast_probability == 1.0
    assert channelled_cast_result == 6

    assert resist_probability == pytest.approx(
        1 / 6
    )
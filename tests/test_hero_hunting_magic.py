"""D1 basic spell resolution: explicitly not a spell-to-kill conversion."""
from types import SimpleNamespace
import pytest
from hero_hunting_magic import calculate_hero_hunting_magic_evidence
from magical_power_resolution_probability import magical_power_effect_probability


def caster():
    assignment = SimpleNamespace(spell=SimpleNamespace(id="TEST_SPELL"), cast_value=4)
    return SimpleNamespace(spells=[assignment])


def evidence(**overrides):
    values = dict(
        caster=caster(), defender=object(), spell_id="TEST_SPELL",
        casting_will_available=3, casting_will_spent=2,
        resistance_will_available=2, resistance_will_spent=1,
        legal_target_confirmed=True, in_range_confirmed=True,
        line_of_sight_confirmed=True,
    )
    values.update(overrides)
    return calculate_hero_hunting_magic_evidence(**values)


def test_cast_and_resist_use_canonical_engine():
    result = evidence()
    assert result.cast_probability == pytest.approx(0.75)
    assert result.effect_probability == pytest.approx(
        magical_power_effect_probability(4, 2, 1)
    )
    assert result.effect_probability < result.cast_probability


def test_spell_effect_is_not_elimination_probability():
    result = evidence()
    assert result.elimination_probability is None
    assert result.evidence_status == "spell_effect_unresolved"
    assert result.dashboard_score is None


def test_unresisted_cast_lands_with_cast_probability():
    result = evidence(resistance_will_spent=0)
    assert result.effect_probability == pytest.approx(result.cast_probability)


def test_resource_accounting_is_explicit():
    result = evidence()
    assert (result.casting_will_remaining, result.resistance_will_remaining) == (1, 1)


@pytest.mark.parametrize("field", [
    "legal_target_confirmed", "in_range_confirmed", "line_of_sight_confirmed"
])
def test_targeting_must_be_confirmed(field):
    with pytest.raises(ValueError, match="target or access"):
        evidence(**{field:False})


def test_unassigned_spell_is_rejected():
    with pytest.raises(ValueError, match="not uniquely assigned"):
        evidence(spell_id="UNKNOWN")


def test_overspend_casting_will_rejected():
    with pytest.raises(ValueError, match="will_spent cannot exceed"):
        evidence(casting_will_spent=4)


def test_overspend_resistance_will_rejected():
    with pytest.raises(ValueError, match="resistance spend exceeds"):
        evidence(resistance_will_spent=3)


def test_boolean_will_is_not_valid():
    with pytest.raises(ValueError, match="non-negative integer"):
        evidence(resistance_will_spent=True)

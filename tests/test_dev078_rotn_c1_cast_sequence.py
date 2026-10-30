"""DEV-078-ROTN-C1: isolated canonical cast sequence acceptance."""
import pytest
from necromancer_cast_sequence import CastDeclaration, validate_cast_sequence

RULE = frozenset({"DG_POWER_OF_THE_NECROMANCER"})


def check(*casts, caster="DG_NEC", rules=RULE):
    return validate_cast_sequence(tuple(casts), caster_profile_id=caster,
                                  active_army_rule_ids=rules)


def cast(spell, target=None, enemy=False):
    return CastDeclaration(spell, target, enemy)


def test_two_distinct_spells_distinct_enemies_allowed():
    assert check(cast("TRANSFIX", "enemy-a", True),
                 cast("SAP_WILL", "enemy-b", True)) is None


def test_repeated_spell_forbidden_even_if_target_changes():
    with pytest.raises(ValueError, match="same power"):
        check(cast("TRANSFIX", "enemy-a", True),
              cast("TRANSFIX", "enemy-b", True))


def test_repeated_enemy_target_forbidden_even_if_spell_changes():
    with pytest.raises(ValueError, match="same enemy"):
        check(cast("TRANSFIX", "enemy-a", True),
              cast("SAP_WILL", "enemy-a", True))


def test_more_than_two_attempts_forbidden():
    with pytest.raises(ValueError, match="activation limit"):
        check(cast("A"), cast("B"), cast("C"))


def test_without_army_rule_only_one_attempt():
    with pytest.raises(ValueError, match="activation limit"):
        check(cast("A"), cast("B"), rules=frozenset())


def test_other_caster_does_not_inherit_two_casts():
    with pytest.raises(ValueError, match="activation limit"):
        check(cast("A"), cast("B"), caster="DG_KHM")


def test_one_spell_without_rule_allowed():
    assert check(cast("A"), rules=frozenset()) is None


def test_friendly_and_enemy_target_same_id_not_enemy_repeat():
    assert check(cast("A", "model-x", True),
                 cast("B", "model-x", False)) is None


def test_non_targeted_spells_supported():
    assert check(cast("A"), cast("B")) is None


def test_enemy_target_requires_id():
    with pytest.raises(ValueError, match="requires"):
        cast("A", enemy=True)

"""DEV-077-GT-C2A source-verified mechanical evidence tests."""
from fractions import Fraction
import pytest
from goblin_king_blubbery_mass import blubbery_mass_evidence


def test_normal_wound_prevented_on_three_plus():
    e = blubbery_mass_evidence(magical_power=False,
            elven_combat_weapon=False, elven_missile_weapon=False)
    assert (e.applicable, e.prevention_target) == (True, 3)
    assert e.prevention_probability == Fraction(2, 3)
    assert e.wound_remaining_probability == Fraction(1, 3)


def test_elven_missile_wound_prevented_on_four_plus():
    e = blubbery_mass_evidence(magical_power=False,
            elven_combat_weapon=False, elven_missile_weapon=True)
    assert e.prevention_target == 4
    assert e.prevention_probability == Fraction(1, 2)


@pytest.mark.parametrize("magic,elf_combat", [(True, False), (False, True), (True, True)])
def test_magical_powers_or_elven_combat_ignore_rule(magic, elf_combat):
    e = blubbery_mass_evidence(magical_power=magic,
            elven_combat_weapon=elf_combat, elven_missile_weapon=False)
    assert e.applicable is False
    assert e.prevention_target is None
    assert e.wound_remaining_probability == 1


@pytest.mark.parametrize("bad", [None, 0, 1, 'unknown'])
def test_unknown_or_nonbool_provenance_is_rejected(bad):
    with pytest.raises(TypeError):
        blubbery_mass_evidence(magical_power=bad,
                elven_combat_weapon=False, elven_missile_weapon=False)

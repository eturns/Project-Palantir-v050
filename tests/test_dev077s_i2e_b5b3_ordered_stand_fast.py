"""B5-B3: explicit activation ordering and special Stand Fast recipients."""
from fractions import Fraction
import pytest

from army_stand_fast_integration import CourageSurvivor, StandFastContact
from army_stand_fast_ordered import OrderedCourageSurvivor, calculate_ordered_stand_fast_resilience
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_classification import HeroicStatus
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule

P = Fraction(21, 36)


def survivor(identifier, index, *, hero=False, race=None, rules=(), courage="7+"):
    profile = Profile(id=identifier, name=identifier, points=10, movement=6,
                      fight=3, shooting="4+", strength=3, defence=4,
                      attacks=1, wounds=1, courage=courage, intelligence="7+",
                      might=0, will=0, fate=0, max_in_army=0,
                      heroic_status=HeroicStatus.HERO if hero else HeroicStatus.WARRIOR)
    if race:
        profile.races.add(race)
    for name in rules:
        profile.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id=name, name=name, category=RuleCategory.SPECIAL)))
    return OrderedCourageSurvivor(CourageSurvivor(identifier, ConfiguredProfile(profile)), index)


def contact(a, b, inches=4, los=True):
    return StandFastContact(a, b, inches, los)


def result(*models, contacts=(), broken=True):
    return calculate_ordered_stand_fast_resilience(models, army_is_broken=broken, contacts=contacts)


def test_hero_before_warrior_grants_conditional_support():
    r = result(survivor("H", 0, hero=True), survivor("W", 1), contacts=(contact("H", "W"),))
    assert r.expected_retained_models == P + (1 - (1-P)**2)


def test_hero_after_warrior_cannot_retroactively_help():
    r = result(survivor("W", 0), survivor("H", 1, hero=True), contacts=(contact("H", "W"),))
    assert r.expected_retained_models == 2 * P


def test_general_of_north_can_support_orc_hero_if_earlier():
    r = result(survivor("AZOG", 0, hero=True, rules=("GENERAL_OF_THE_NORTH",)),
               survivor("ORC_HERO", 1, hero=True, race="ORC"),
               contacts=(contact("AZOG", "ORC_HERO", 10),))
    assert r.expected_retained_models == P + (1 - (1-P)**2)


def test_general_of_north_cannot_support_non_orc_hero():
    r = result(survivor("AZOG", 0, hero=True, rules=("GENERAL_OF_THE_NORTH",)),
               survivor("MAN_HERO", 1, hero=True, race="MAN"),
               contacts=(contact("AZOG", "MAN_HERO"),))
    assert r.expected_retained_models == 2*P


def test_ordinary_hero_cannot_support_second_hero():
    r = result(survivor("H1", 0, hero=True), survivor("H2", 1, hero=True),
               contacts=(contact("H1", "H2"),))
    assert r.expected_retained_models == 2*P


def test_cascaded_hero_support_preserves_dependency():
    # AZOG -> ORC hero -> Warrior. Shared upstream Hero outcome is not
    # treated as an independent roll at each downstream edge.
    r = result(survivor("AZOG", 0, hero=True, rules=("GENERAL_OF_THE_NORTH",)),
               survivor("CAPTAIN", 1, hero=True, race="ORC"),
               survivor("W", 2),
               contacts=(contact("AZOG", "CAPTAIN"), contact("CAPTAIN", "W")))
    assert r.expected_retained_models == P + (P + (1-P)*P) + (1 - (1-P)*(1-P)**2)


def test_dead_or_missing_provider_is_not_assumed():
    with pytest.raises(ValueError, match="unknown survivor"):
        result(survivor("W", 0), contacts=(contact("DEAD_HERO", "W"),))


def test_fearless_provider_supports_after_activation_not_before():
    r = result(survivor("W1", 0), survivor("H", 1, hero=True, rules=("FEARLESS",)),
               survivor("W2", 2),
               contacts=(contact("H", "W1"), contact("H", "W2")))
    assert r.expected_retained_models == P + 1 + 1


def test_los_is_still_required_for_special_hero_recipient():
    r = result(survivor("AZOG", 0, hero=True, rules=("GENERAL_OF_THE_NORTH",)),
               survivor("CAPTAIN", 1, hero=True, race="ORC"),
               contacts=(contact("AZOG", "CAPTAIN", 4, False),))
    assert r.expected_retained_models == 2*P


def test_duplicate_activation_indices_rejected():
    with pytest.raises(ValueError, match="Activation indices"):
        result(survivor("H", 0, hero=True), survivor("W", 0))


def test_unbroken_returns_all_survivors():
    r = result(survivor("W", 0), survivor("H", 1, hero=True), broken=False)
    assert r.expected_retained_models == 2
    assert r.expected_fleeing_models == 0


def test_empty_army_is_defined():
    r = result()
    assert r.surviving_model_count == 0
    assert r.retention_fraction == 0

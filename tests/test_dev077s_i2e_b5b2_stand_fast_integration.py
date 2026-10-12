"""B5-B2: Stand Fast coverage must be explicit, conditional, and non-duplicated."""
from fractions import Fraction
import pytest
from army_stand_fast_integration import (
    CourageSurvivor, StandFastContact, calculate_positioned_broken_courage_resilience,
)
from configured_profile import ConfiguredProfile
from profile_classification import HeroicStatus
from profiles import Profile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from special_rule import SpecialRule


def model(identifier, *, heroic_status=HeroicStatus.WARRIOR, courage="7+", rules=()):
    p = Profile(id=identifier, name=identifier, points=10, movement=6,
        fight=3, shooting="4+", strength=3, defence=4, attacks=1, wounds=1,
        courage=courage, intelligence="7+", might=0, will=0, fate=0,
        max_in_army=0, heroic_status=heroic_status)
    for rule in rules:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id=rule, name=rule, category=RuleCategory.SPECIAL)))
    return CourageSurvivor(identifier, ConfiguredProfile(p))


def retention(*survivors, contacts=(), broken=True):
    return calculate_positioned_broken_courage_resilience(
        survivors, army_is_broken=broken, contacts=contacts)


def contact(a="H", b="W", distance=4, los=True):
    return StandFastContact(a, b, distance, los)


def test_no_contacts_does_not_infer_stand_fast():
    r = retention(model("H", heroic_status=HeroicStatus.HERO), model("W"))
    assert r.expected_retained_models == Fraction(42, 36)


def test_verified_contact_includes_provider_success_probability():
    r = retention(model("H", heroic_status=HeroicStatus.HERO), model("W"),
                  contacts=(contact(),))
    expected_w = 1 - Fraction(15, 36) * Fraction(15, 36)
    assert r.expected_retained_models == Fraction(21, 36) + expected_w


def test_out_of_range_and_no_los_do_not_grant_support():
    survivors = (model("H", heroic_status=HeroicStatus.HERO), model("W"))
    for c in (contact(distance=6.1), contact(los=False)):
        assert retention(*survivors, contacts=(c,)).expected_retained_models == Fraction(42, 36)


def test_exact_six_inches_is_eligible():
    survivors = (model("H", heroic_status=HeroicStatus.HERO), model("W"))
    assert retention(*survivors, contacts=(contact(distance=6),)).expected_retained_models > Fraction(42, 36)


def test_shared_provider_does_not_duplicate_hero_test():
    survivors = (model("H", heroic_status=HeroicStatus.HERO), model("W"), model("W2"))
    result = retention(*survivors, contacts=(contact(), contact("H", "W2")))
    warrior_pass = 1 - Fraction(15, 36)**2
    assert result.expected_retained_models == Fraction(21, 36) + 2 * warrior_pass


def test_two_providers_have_distinct_success_events():
    survivors = (model("H", heroic_status=HeroicStatus.HERO),
                 model("H2", heroic_status=HeroicStatus.HERO), model("W"))
    r = retention(*survivors, contacts=(contact(), contact("H2", "W")))
    assert r.expected_retained_models == 2*Fraction(21,36) + (1-Fraction(15,36)**3)


def test_warrior_cannot_provide_stand_fast():
    r = retention(model("H"), model("W"), contacts=(contact(),))
    assert r.expected_retained_models == Fraction(42,36)


def test_automatons_provider_rejected():
    r = retention(model("H", heroic_status=HeroicStatus.HERO, rules=("AUTOMATONS",)),
                  model("W"), contacts=(contact(),))
    assert r.expected_retained_models == Fraction(42,36)


def test_fearless_provider_supports_warrior_with_certainty():
    r = retention(model("H", heroic_status=HeroicStatus.HERO, rules=("FEARLESS",)),
                  model("W"), contacts=(contact(),))
    assert r.expected_retained_models == Fraction(2)


def test_unbroken_force_has_no_fleeing_models():
    r = retention(model("H", heroic_status=HeroicStatus.HERO), model("W"), broken=False)
    assert r.expected_retained_models == 2
    assert r.expected_fleeing_models == 0


def test_unknown_model_contact_is_rejected():
    with pytest.raises(ValueError, match="unknown survivor"):
        retention(model("H", heroic_status=HeroicStatus.HERO), contacts=(contact(),))


def test_negative_contact_distance_is_rejected():
    with pytest.raises(ValueError, match="negative"):
        retention(model("H", heroic_status=HeroicStatus.HERO), model("W"),
                  contacts=(contact(distance=-1),))

"""DEV-077S-I2-E-B4-H: fielded Courage state boundary tests.

Characterisation-first: passing tests confirm existing mechanics; failures
identify genuine integration gaps. No arbitrary scoring assumptions.
"""
from dataclasses import replace
from fractions import Fraction

from configured_profile import ConfiguredProfile
from contextual_courage import (
    CouragePositionContext,
    calculate_contextual_courage_success_probability,
)
from courage_test import calculate_courage_test_success_probability
from database.rule_category import RuleCategory
from fielded_model import FieldedModel
from fielded_model_form_state import FieldedModelFormState
from fielded_model_form_transition import change_fielded_model_form
from mount import Mount
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule


def make_profile(identifier, *, courage="7+", rules=(), mount=None):
    profile = Profile(
        id=identifier, name=identifier, points=10, movement=6,
        fight=3, shooting="4+", strength=3, defence=4,
        attacks=1, wounds=1, courage=courage, intelligence="7+",
        might=0, will=0, fate=0, max_in_army=0,
        default_mount=mount,
    )
    for rule_id in rules:
        profile.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id=rule_id, name=rule_id, category=RuleCategory.SPECIAL,
            )
        ))
    return ConfiguredProfile(profile=profile)


def make_mount(*, fearless=False):
    return Mount(
        id="MOUNT", name="Mount", movement=10, fight=3,
        shooting="6+", strength=3, defence=4, attacks=1, wounds=1,
        courage="7+", intelligence="7+", base_size_mm=40,
        special_rule_ids=(
            frozenset({"FEARLESS"}) if fearless else frozenset()
        ),
    )


def state(configured, *, alternate_ids=()):
    fielded = FieldedModel(id="UNIT:1", configured_profile=configured)
    return FieldedModelFormState(
        fielded_model=fielded,
        active_configured_profile=configured,
        allowed_alternate_profile_ids=frozenset(alternate_ids),
    )


def test_active_fearless_mount_grants_automatic_courage_pass():
    rider = make_profile("RIDER", mount=make_mount(fearless=True))
    mounted = state(rider)
    assert calculate_courage_test_success_probability(mounted) == Fraction(1)


def test_losing_fearless_mount_restores_rider_courage():
    rider = make_profile("RIDER", mount=make_mount(fearless=True))
    mounted = state(rider)
    dismounted = replace(mounted, mount_active=False)
    assert calculate_courage_test_success_probability(mounted) == Fraction(1)
    assert calculate_courage_test_success_probability(dismounted) == Fraction(21, 36)


def test_rider_intrinsic_fearless_remains_after_dismount():
    rider = make_profile("RIDER", rules=("FEARLESS",), mount=make_mount())
    dismounted = replace(state(rider), mount_active=False)
    assert calculate_courage_test_success_probability(dismounted) == Fraction(1)


def test_active_form_not_original_profile_sets_courage_target():
    original = make_profile("NORMAL", courage="7+")
    alternate = make_profile("ALTERNATE", courage="4+")
    original_state = state(original, alternate_ids=("ALTERNATE",))
    transformed = change_fielded_model_form(original_state, alternate)
    assert calculate_courage_test_success_probability(original_state) == Fraction(21, 36)
    assert calculate_courage_test_success_probability(transformed) == Fraction(33, 36)
    assert transformed.fielded_model_id == original_state.fielded_model_id


def test_active_form_fearless_is_not_inherited_from_original_form():
    original = make_profile("ORIGINAL", rules=("FEARLESS",))
    alternate = make_profile("ALTERNATE")
    transformed = change_fielded_model_form(
        state(original, alternate_ids=("ALTERNATE",)), alternate,
    )
    assert calculate_courage_test_success_probability(transformed) == Fraction(21, 36)


def test_alternate_form_gains_its_own_fearless_rule():
    original = make_profile("ORIGINAL")
    alternate = make_profile("ALTERNATE", rules=("FEARLESS",))
    transformed = change_fielded_model_form(
        state(original, alternate_ids=("ALTERNATE",)), alternate,
    )
    assert calculate_courage_test_success_probability(transformed) == Fraction(1)


def test_bound_in_shadow_uses_current_form_only():
    original = make_profile("ORIGINAL", rules=("BOUND_IN_SHADOW",))
    alternate = make_profile("ALTERNATE")
    start = state(original, alternate_ids=("ALTERNATE",))
    changed = change_fielded_model_form(start, alternate)
    nearby = CouragePositionContext(distance_to_friendly_ringwraith_inches=3)
    assert calculate_contextual_courage_success_probability(
        start, position_context=nearby,
    ) == Fraction(1)
    assert calculate_contextual_courage_success_probability(
        changed, position_context=nearby,
    ) == Fraction(21, 36)


def test_bound_in_shadow_switches_off_when_support_is_lost():
    configured = make_profile("CASTELLAN", courage="7+",
                              rules=("BOUND_IN_SHADOW",))
    active = state(configured)
    nearby = CouragePositionContext(distance_to_sauron_inches=6)
    distant = CouragePositionContext(distance_to_sauron_inches=6.1)
    assert calculate_contextual_courage_success_probability(
        active, position_context=nearby,
    ) == Fraction(1)
    assert calculate_contextual_courage_success_probability(
        active, position_context=distant,
    ) == Fraction(21, 36)

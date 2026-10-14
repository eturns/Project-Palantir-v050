"""G3-D2 tests using the real production import fixtures (no invented rolls)."""
import pytest
from army import Army
from hero_hunting_real_opportunities import collect_real_attack_opportunities
from tests.test_dev077s_i2f_f4_a2_real_army_magic import real_armies as fixture_armies


@pytest.fixture(scope="module")
def real_armies(fixture_armies):
    return fixture_armies


def test_rise_has_real_necromancer_spell_capabilities(real_armies):
    (rise, _), _ = real_armies
    result = collect_real_attack_opportunities("rise", rise)
    spells = {c.source_id for c in result.capabilities if c.method == "magic"}
    assert {"COMPEL", "CHILL_SOUL", "YOUR_STAFF_IS_BROKEN"} <= spells


def test_magic_requires_resource_and_target_validation(real_armies):
    (rise, _), _ = real_armies
    result = collect_real_attack_opportunities("rise", rise)
    assert all("casting_resources" in c.unresolved_conditions and
               c.maximum_nominal_uses is None for c in result.capabilities if c.method == "magic")


def test_real_azog_hunters_melee_identity_per_copy(real_armies):
    _, (hunters, _) = real_armies
    result = collect_real_attack_opportunities("hunters", hunters)
    melee = [c for c in result.capabilities if c.method == "melee"]
    assert melee and len({c.model_id for c in melee}) == len(melee)


def test_melee_is_not_assumed_in_range(real_armies):
    _, (hunters, _) = real_armies
    result = collect_real_attack_opportunities("hunters", hunters)
    assert all("engagement" in c.unresolved_conditions and
               c.maximum_nominal_uses is None for c in result.capabilities if c.method == "melee")


def test_all_candidates_have_unique_method_source_keys(real_armies):
    (rise, _), (hunters, _) = real_armies
    for label, army in (("rise", rise), ("hunters", hunters)):
        result = collect_real_attack_opportunities(label, army)
        keys = [(x.model_id, x.method, x.source_id) for x in result.capabilities]
        assert len(keys) == len(set(keys))


def test_no_unearned_executable_status(real_armies):
    (rise, _), _ = real_armies
    result = collect_real_attack_opportunities("rise", rise)
    assert all(c.capability_status != "executable" for c in result.capabilities)


def test_no_probability_or_dashboard_score(real_armies):
    (rise, _), _ = real_armies
    result = collect_real_attack_opportunities("rise", rise)
    assert result.dashboard_score is None and result.scenario_score is None
    assert not hasattr(result, "elimination_probability")


def test_empty_army_no_opportunities():
    result = collect_real_attack_opportunities("empty", Army())
    assert result.capabilities == () and result.unresolved == ()


def test_invalid_army_rejected():
    with pytest.raises(TypeError):
        collect_real_attack_opportunities("invalid", object())


def test_invalid_label_rejected():
    with pytest.raises(ValueError):
        collect_real_attack_opportunities("", Army())


def test_separate_armies_have_separate_model_ids(real_armies):
    (rise, _), (hunters, _) = real_armies
    a = collect_real_attack_opportunities("rise", rise)
    b = collect_real_attack_opportunities("hunters", hunters)
    assert {x.model_id for x in a.capabilities}.isdisjoint(x.model_id for x in b.capabilities)


def test_no_mutation_of_production_armies(real_armies):
    (rise, _), _ = real_armies
    pts = rise.total_points()
    collect_real_attack_opportunities("rise", rise)
    assert rise.total_points() == pts


def test_shooting_profiles_are_not_invented(real_armies):
    (rise, _), (hunters, _) = real_armies
    from ranged_weapon_profile import RANGED_WEAPON_PROFILES
    for label, army in (("rise", rise), ("hunters", hunters)):
        r = collect_real_attack_opportunities(label, army)
        assert all(c.source_id in RANGED_WEAPON_PROFILES
                   for c in r.capabilities if c.method == "shooting")


def test_shooting_remains_conditional(real_armies):
    _, (hunters, _) = real_armies
    r = collect_real_attack_opportunities("hunters", hunters)
    assert all("range" in c.unresolved_conditions and
               "line_of_sight" in c.unresolved_conditions for c in r.capabilities if c.method == "shooting")

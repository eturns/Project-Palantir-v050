"""DEV-077S-I2-D-C4: non-scoring mobility independence and sensitivity tests.

Tests use existing mechanics and aggregation. They do not alter app scoring.
"""
import pytest

from army import Army
from profiles import Profile
from special_rule import SpecialRule
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from ability_tag_entity import AbilityTagEntity
from ability_tag_assignment import AbilityTagAssignment
from army_mobility_aggregation import aggregate_army_mobility
from mobility_mechanical_comparison import compare_army_mobility
from reposition_mechanics import (
    RepositionRequest, RepositionTiming, RepositionUsage,
    spiritual_displacement_rule, validate_reposition, apply_reposition,
)


def model(name, *, move=6, base=25, points=20, rules=()):
    p = Profile(
        id=name, name=name, points=points, movement=move, base_size_mm=base,
        fight=3, shooting="4+", strength=3, defence=4, attacks=1,
        wounds=1, courage="6+", intelligence="7+", might=0, will=0,
        fate=0, max_in_army=0,
    )
    for rule_id, weight in rules:
        rule = SpecialRule(id=rule_id, name=rule_id, category=RuleCategory.MOVEMENT)
        if weight is not None:
            rule.ability_tags.append(
                AbilityTagAssignment(
                    tag=AbilityTagEntity(id="MOBILITY", name="Mobility"),
                    weight=weight,
                )
            )
        p.special_rules.append(ProfileSpecialRuleAssignment(rule=rule))
    return p


def army_of(profile, quantity=1):
    a = Army()
    a.add_profile(profile, quantity=quantity)
    return a


@pytest.mark.parametrize("rule_id,weight", [
    ("UNNATURAL_SPEED", 1.5),
    ("SPECTRAL_WALK", 1.5),
    ("SWIFT_MOVEMENT", 1.25),
])
def test_legacy_bonus_never_leaks_into_open_ground(rule_id, weight):
    base = aggregate_army_mobility(army_of(model("BASE")))
    tagged = aggregate_army_mobility(
        army_of(model("TAGGED", rules=((rule_id, weight),)))
    )
    assert tagged.average_open_ground == pytest.approx(base.average_open_ground)
    assert tagged.legacy_average == pytest.approx(base.legacy_average + weight)


@pytest.mark.parametrize("rule_id", ["SPECTRAL_WALK", "SWIFT_MOVEMENT"])
def test_terrain_rule_affects_only_appropriate_terrain_measure(rule_id):
    ordinary = aggregate_army_mobility(army_of(model("REG")))
    terrain = aggregate_army_mobility(
        army_of(model("SPECIAL", rules=((rule_id, 1.25),)))
    )
    assert terrain.average_open_ground == pytest.approx(ordinary.average_open_ground)
    assert terrain.average_difficult_terrain > ordinary.average_difficult_terrain
    assert terrain.terrain_retention == pytest.approx(1.0)


def test_paired_ability_does_not_change_mechanical_open_ground():
    alone = aggregate_army_mobility(
        army_of(model("KNIGHT", rules=(("SPIRITUAL_DISPLACEMENT", 1.5),)))
    )
    paired = aggregate_army_mobility(
        army_of(model("KNIGHT2", rules=(("SPIRITUAL_DISPLACEMENT", 1.5),)), 2)
    )
    assert alone.average_open_ground == pytest.approx(paired.average_open_ground)
    assert alone.eligible_anchor_pairs == 0
    assert paired.eligible_anchor_pairs == 1
    assert paired.legacy_average > alone.legacy_average
    assert paired.reposition_requires_context


def test_quantity_changes_collective_output_not_mean_or_efficiency():
    one = aggregate_army_mobility(army_of(model("ONE", points=20), 1))
    many = aggregate_army_mobility(army_of(model("MANY", points=20), 4))
    assert many.average_open_ground == pytest.approx(one.average_open_ground)
    assert many.total_open_ground == pytest.approx(4 * one.total_open_ground)
    assert many.open_ground_per_100_points == pytest.approx(one.open_ground_per_100_points)


def test_base_size_reduces_accessibility_without_changing_printed_move():
    small = aggregate_army_mobility(army_of(model("SMALL", base=25)))
    big = aggregate_army_mobility(army_of(model("BIG", base=60)))
    assert small.average_open_ground == pytest.approx(6)
    assert big.average_open_ground < small.average_open_ground
    assert big.average_difficult_terrain < small.average_difficult_terrain


def test_points_cost_changes_density_not_average_mobility():
    cheap = aggregate_army_mobility(army_of(model("CHEAP", points=10)))
    dear = aggregate_army_mobility(army_of(model("DEAR", points=40)))
    assert cheap.average_open_ground == pytest.approx(dear.average_open_ground)
    assert cheap.open_ground_per_100_points == pytest.approx(
        4 * dear.open_ground_per_100_points
    )


def test_two_eligible_knights_do_not_guarantee_legal_reposition():
    pair = compare_army_mobility(
        army_of(model("AK", rules=(("SPIRITUAL_DISPLACEMENT", 1.5),)), 2)
    )
    assert pair.eligible_anchor_pairs == 1
    usage = RepositionUsage()
    usage.begin_turn(1)
    request = RepositionRequest(
        actor_id="AK-1", anchor_id="AK-2",
        origin=(0.0, 0.0), anchor_position=(12.0, 0.0),
        destination=(13.0, 0.0),
        timing=RepositionTiming.PRE_HEROIC_ACTIONS,
        anchor_is_eligible=True, legal_placement=False,
    )
    valid, reason = validate_reposition(spiritual_displacement_rule(), request, usage)
    assert not valid
    assert "placement" in reason.lower()


def test_abyssal_knights_one_shared_activation_per_turn():
    rule = spiritual_displacement_rule()
    usage = RepositionUsage()
    usage.begin_turn(1)
    def request(actor, anchor):
        return RepositionRequest(
            actor_id=actor, anchor_id=anchor, origin=(0.0, 0.0),
            anchor_position=(12.0, 0.0), destination=(13.0, 0.0),
            timing=RepositionTiming.PRE_HEROIC_ACTIONS,
            anchor_is_eligible=True,
        )
    apply_reposition(rule, request("AK-1", "AK-2"), usage)
    valid, _ = validate_reposition(rule, request("AK-2", "AK-1"), usage)
    assert not valid
    usage.begin_turn(2)
    valid, _ = validate_reposition(rule, request("AK-2", "AK-1"), usage)
    assert valid

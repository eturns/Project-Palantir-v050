from army import Army
from optimiser_candidate import OptimiserCandidate
from objective_score import (
    ObjectiveContribution,
    ObjectiveScore,
)
from profiles import Profile
from scenario_validation_record import (
    ScenarioValidationRecord,
    build_scenario_validation_record,
    build_scenario_validation_records,
    rank_scenario_validation_records,
    scenario_validation_extremes,
)


class FakeScenarioObjective:
    def score(
        self,
        candidate,
    ):
        return ObjectiveScore(
            total=0.625,
            contributions=(
                ObjectiveContribution(
                    name="hold_objective",
                    value=0.7,
                ),
                ObjectiveContribution(
                    name="kill_the_enemy",
                    value=0.6,
                ),
                ObjectiveContribution(
                    name="maelstrom_of_battle",
                    value=0.5,
                ),
                ObjectiveContribution(
                    name="object",
                    value=0.4,
                ),
                ObjectiveContribution(
                    name="manoeuvring",
                    value=0.8,
                ),
                ObjectiveContribution(
                    name="unique",
                    value=0.75,
                ),
            ),
        )


def test_build_scenario_validation_record_captures_candidate_score_and_pools():
    profile = Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=100,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=2,
        will=2,
        fate=2,
        max_in_army=2,
    )

    army = Army()

    army.add_profile(
        profile,
        quantity=2,
    )

    candidate = OptimiserCandidate(
        army=army,
    )

    record = build_scenario_validation_record(
        candidate=candidate,
        objective=FakeScenarioObjective(),
    )

    assert record.candidate is candidate

    assert record.composition == (
        (
            "TEST_PROFILE",
            2,
        ),
    )

    assert record.total_score == 0.625

    assert record.pool_scores == (
        (
            "hold_objective",
            0.7,
        ),
        (
            "kill_the_enemy",
            0.6,
        ),
        (
            "maelstrom_of_battle",
            0.5,
        ),
        (
            "object",
            0.4,
        ),
        (
            "manoeuvring",
            0.8,
        ),
        (
            "unique",
            0.75,
        ),
    )

def test_build_scenario_validation_records_builds_one_record_per_candidate():
    profile = Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=100,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=2,
        will=2,
        fate=2,
        max_in_army=2,
    )

    first_army = Army()
    first_army.add_profile(
        profile,
        quantity=1,
    )

    second_army = Army()
    second_army.add_profile(
        profile,
        quantity=2,
    )

    candidates = (
        OptimiserCandidate(
            army=first_army,
        ),
        OptimiserCandidate(
            army=second_army,
        ),
    )

    records = build_scenario_validation_records(
        candidates=candidates,
        objective=FakeScenarioObjective(),
    )

    assert len(records) == 2

    assert records[0].candidate is candidates[0]
    assert records[1].candidate is candidates[1]

    assert records[0].composition == (
        (
            "TEST_PROFILE",
            1,
        ),
    )

    assert records[1].composition == (
        (
            "TEST_PROFILE",
            2,
        ),
    )

def test_rank_scenario_validation_records_orders_descending_and_preserves_ties():
    profile = Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=100,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=2,
        will=2,
        fate=2,
        max_in_army=3,
    )

    first_army = Army()
    first_army.add_profile(
        profile,
        quantity=1,
    )

    second_army = Army()
    second_army.add_profile(
        profile,
        quantity=2,
    )

    third_army = Army()
    third_army.add_profile(
        profile,
        quantity=3,
    )

    first_candidate = OptimiserCandidate(
        army=first_army,
    )

    second_candidate = OptimiserCandidate(
        army=second_army,
    )

    third_candidate = OptimiserCandidate(
        army=third_army,
    )

    from scenario_validation_record import (
        ScenarioValidationRecord,
    )

    first_record = ScenarioValidationRecord(
        candidate=first_candidate,
        composition=(("TEST_PROFILE", 1),),
        total_score=0.5,
        pool_scores=(),
    )

    second_record = ScenarioValidationRecord(
        candidate=second_candidate,
        composition=(("TEST_PROFILE", 2),),
        total_score=0.8,
        pool_scores=(),
    )

    third_record = ScenarioValidationRecord(
        candidate=third_candidate,
        composition=(("TEST_PROFILE", 3),),
        total_score=0.5,
        pool_scores=(),
    )

    records = (
        first_record,
        second_record,
        third_record,
    )

    ranked = rank_scenario_validation_records(
        records,
    )

    assert ranked == (
        second_record,
        first_record,
        third_record,
    )

def test_scenario_validation_extremes_returns_top_and_bottom_records():
    profile = Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=100,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=2,
        will=2,
        fate=2,
        max_in_army=5,
    )

    records = []

    for quantity, score in (
        (1, 0.9),
        (2, 0.8),
        (3, 0.7),
        (4, 0.6),
        (5, 0.5),
    ):
        army = Army()

        army.add_profile(
            profile,
            quantity=quantity,
        )

        candidate = OptimiserCandidate(
            army=army,
        )

        records.append(
            ScenarioValidationRecord(
                candidate=candidate,
                composition=(
                    (
                        "TEST_PROFILE",
                        quantity,
                    ),
                ),
                total_score=score,
                pool_scores=(),
            )
        )

    ranked = rank_scenario_validation_records(
        tuple(records),
    )

    top, bottom = scenario_validation_extremes(
        ranked,
        count=2,
    )

    assert top == (
        ranked[0],
        ranked[1],
    )

    assert bottom == (
        ranked[-2],
        ranked[-1],
    )
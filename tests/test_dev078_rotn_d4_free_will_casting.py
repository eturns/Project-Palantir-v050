"""DEV-078-ROTN-D4: explicit resource-ledger and free casting die tests."""
import pytest
from necromancer_free_will_casting import (
    FundedCastRequest, assess_necromancer_funded_casts,
)

BOTH = ("DG_POWER_OF_THE_NECROMANCER", "DG_HIS_SPIRIT")


def req(spell="TRANSFIX", target="ENEMY:1", spent=1, threshold=4):
    return FundedCastRequest(spell, target, threshold, spent)


def assess(requests, *, profile="DG_NEC", rules=BOTH, will=3):
    return assess_necromancer_funded_casts(
        profile_id=profile, active_army_rule_ids=rules,
        initial_will=will, requests=requests,
    )


def test_free_die_does_not_spend_will():
    result = assess([req()])
    assert result.casts[0].cast.additional_dice == 1
    assert result.casts[0].cast.dice_total == 2
    assert result.remaining_will == 2


def test_two_casts_have_separate_free_dice_and_shared_will_ledger():
    result = assess([req(spent=2), req("COMPEL", "ENEMY:2", spent=1)])
    assert [c.will_before for c in result.casts] == [3, 1]
    assert [c.will_after for c in result.casts] == [1, 0]
    assert [c.cast.dice_total for c in result.casts] == [3, 2]


def test_other_caster_does_not_gain_die():
    result = assess([req()], profile="OTHER")
    assert result.casts[0].cast.additional_dice == 0
    assert result.rule_id is None


def test_missing_rule_does_not_gain_die():
    result = assess([req()], rules=("DG_POWER_OF_THE_NECROMANCER",))
    assert result.casts[0].cast.additional_dice == 0


def test_own_army_rule_required_for_second_cast():
    with pytest.raises(ValueError, match="too many"):
        assess([req(), req("COMPEL", "ENEMY:2")], rules=("DG_HIS_SPIRIT",))


@pytest.mark.parametrize("requests,pattern", [
    ([req(), req()], "same spell"),
    ([req(), req("COMPEL")], "same enemy"),
])
def test_duplicate_sequence_rejected(requests, pattern):
    with pytest.raises(ValueError, match=pattern):
        assess(requests)


def test_insufficient_will_rejected_before_second_cast():
    with pytest.raises(ValueError, match="cannot exceed"):
        assess([req(spent=3), req("COMPEL", "ENEMY:2")])


def test_zero_will_cannot_use_free_die_alone():
    with pytest.raises(ValueError, match="cannot exceed"):
        assess([req()], will=0)


def test_empty_sequence_reports_no_spending():
    report = assess([])
    assert report.remaining_will == 3
    assert report.casts == ()
    assert report.dashboard_score is None and report.scenario_score is None


def test_probability_is_existing_engine_evidence():
    report = assess([req(threshold=4)])
    assert report.casts[0].cast.probability == pytest.approx(0.75)

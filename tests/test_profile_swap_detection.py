from army import Army
from optimiser_candidate import OptimiserCandidate
from profile_swap import ProfileSwap
from profile_swap_detection import detect_profile_swap
from profiles import Profile


def make_profile(
    profile_id: str,
    *,
    points: int = 80,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=points,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def make_candidate(
    entries: tuple[tuple[Profile, int], ...],
) -> OptimiserCandidate:
    army = Army()

    for profile, quantity in entries:
        army.add_profile(
            profile,
            quantity=quantity,
        )

    return OptimiserCandidate(
        army=army,
    )


def test_detect_profile_swap_returns_removed_and_added_profile():
    profile_a = make_profile("nazgul_a")
    profile_b = make_profile("nazgul_b")
    profile_c = make_profile("nazgul_c")

    original = make_candidate(
        (
            (profile_a, 1),
            (profile_b, 1),
        )
    )

    alternative = make_candidate(
        (
            (profile_a, 1),
            (profile_c, 1),
        )
    )

    assert detect_profile_swap(
        original,
        alternative,
    ) == ProfileSwap(
        removed_profile_id="nazgul_b",
        added_profile_id="nazgul_c",
    )


def test_detect_profile_swap_handles_quantity_reduction_without_profile_removal():
    profile_a = make_profile("nazgul_a")
    profile_b = make_profile("nazgul_b")

    original = make_candidate(
        (
            (profile_a, 2),
            (profile_b, 1),
        )
    )

    alternative = make_candidate(
        (
            (profile_a, 1),
            (profile_b, 2),
        )
    )

    assert detect_profile_swap(
        original,
        alternative,
    ) == ProfileSwap(
        removed_profile_id="nazgul_a",
        added_profile_id="nazgul_b",
    )


def test_detect_profile_swap_returns_none_when_candidates_are_identical():
    profile_a = make_profile("nazgul_a")

    original = make_candidate(
        (
            (profile_a, 1),
        )
    )

    alternative = make_candidate(
        (
            (profile_a, 1),
        )
    )

    assert detect_profile_swap(
        original,
        alternative,
    ) is None


def test_detect_profile_swap_returns_none_when_more_than_one_model_changes():
    profile_a = make_profile("nazgul_a")
    profile_b = make_profile("nazgul_b")
    profile_c = make_profile("nazgul_c")
    profile_d = make_profile("nazgul_d")

    original = make_candidate(
        (
            (profile_a, 1),
            (profile_b, 1),
        )
    )

    alternative = make_candidate(
        (
            (profile_c, 1),
            (profile_d, 1),
        )
    )

    assert detect_profile_swap(
        original,
        alternative,
    ) is None


def test_detect_profile_swap_returns_none_when_model_count_changes():
    profile_a = make_profile("nazgul_a")
    profile_b = make_profile("nazgul_b")

    original = make_candidate(
        (
            (profile_a, 1),
        )
    )

    alternative = make_candidate(
        (
            (profile_a, 1),
            (profile_b, 1),
        )
    )

    assert detect_profile_swap(
        original,
        alternative,
    ) is None
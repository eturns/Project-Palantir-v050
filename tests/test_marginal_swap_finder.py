from army import Army
from optimiser_candidate import OptimiserCandidate
from marginal_swap_finder import find_marginal_alternatives
from profiles import Profile


def make_profile(
    profile_id: str,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=80,
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


def test_find_marginal_alternatives_returns_only_one_swap_candidates():
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

    one_swap = make_candidate(
        (
            (profile_a, 1),
            (profile_c, 1),
        )
    )

    two_swaps = make_candidate(
        (
            (profile_c, 1),
            (profile_d, 1),
        )
    )

    alternatives = find_marginal_alternatives(
        original,
        (
            one_swap,
            two_swaps,
        ),
    )

    assert alternatives == (
        one_swap,
    )


def test_find_marginal_alternatives_excludes_original_candidate():
    profile_a = make_profile("nazgul_a")
    profile_b = make_profile("nazgul_b")

    original = make_candidate(
        (
            (profile_a, 1),
            (profile_b, 1),
        )
    )

    alternatives = find_marginal_alternatives(
        original,
        (
            original,
        ),
    )

    assert alternatives == ()


def test_find_marginal_alternatives_preserves_candidate_pool_order():
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

    first_alternative = make_candidate(
        (
            (profile_a, 1),
            (profile_c, 1),
        )
    )

    second_alternative = make_candidate(
        (
            (profile_a, 1),
            (profile_d, 1),
        )
    )

    alternatives = find_marginal_alternatives(
        original,
        (
            first_alternative,
            second_alternative,
        ),
    )

    assert alternatives == (
        first_alternative,
        second_alternative,
    )


def test_find_marginal_alternatives_returns_empty_tuple_when_none_exist():
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

    unrelated = make_candidate(
        (
            (profile_c, 1),
            (profile_d, 1),
        )
    )

    assert find_marginal_alternatives(
        original,
        (
            unrelated,
        ),
    ) == ()
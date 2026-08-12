from army import Army
from optimiser_candidate import OptimiserCandidate
from optimiser_candidate_key import (
    build_candidate_key,
)
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


def test_build_candidate_key_uses_profile_ids_and_quantities():
    profile_a = make_profile("nazgul_a")
    profile_b = make_profile("nazgul_b")

    candidate = make_candidate(
        (
            (profile_a, 1),
            (profile_b, 2),
        )
    )

    assert build_candidate_key(
        candidate,
    ) == "nazgul_a:1|nazgul_b:2"


def test_build_candidate_key_is_independent_of_entry_order():
    profile_a = make_profile("nazgul_a")
    profile_b = make_profile("nazgul_b")

    first = make_candidate(
        (
            (profile_a, 1),
            (profile_b, 2),
        )
    )

    second = make_candidate(
        (
            (profile_b, 2),
            (profile_a, 1),
        )
    )

    assert build_candidate_key(
        first,
    ) == build_candidate_key(
        second,
    )


def test_build_candidate_key_distinguishes_different_quantities():
    profile_a = make_profile("nazgul_a")

    one_copy = make_candidate(
        (
            (profile_a, 1),
        )
    )

    two_copies = make_candidate(
        (
            (profile_a, 2),
        )
    )

    assert build_candidate_key(
        one_copy,
    ) != build_candidate_key(
        two_copies,
    )


def test_build_candidate_key_returns_empty_string_for_empty_army():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    assert build_candidate_key(
        candidate,
    ) == ""
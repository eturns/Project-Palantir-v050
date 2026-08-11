from composition_enumerator import (
    build_candidate,
    enumerate_legal_quantity_candidates,
    enumerate_profile_quantities,
    enumerate_quantity_candidates,
    enumerate_repeated_selections,
    enumerate_selections,
    filter_legal_candidates,
)
from profiles import Profile
from profiles import Profile

def create_test_profile(
    profile_id: str,
    points: int = 10,
    max_in_army: int = 1,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=points,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=max_in_army,
    )

def test_enumerate_selections_generates_unique_fixed_size_combinations():
    items = (
        "A",
        "B",
        "C",
    )

    selections = enumerate_selections(
        items=items,
        selection_size=2,
    )

    assert selections == (
        ("A", "B"),
        ("A", "C"),
        ("B", "C"),
    )

def test_build_candidate_creates_army_from_profile_selection():
    first_profile = create_test_profile(
        "FIRST",
        points=20,
    )

    second_profile = create_test_profile(
        "SECOND",
        points=30,
    )

    candidate = build_candidate(
        (
            first_profile,
            second_profile,
        )
    )

    assert candidate.army.profile_count() == 2
    assert candidate.army.total_points() == 50

    assert candidate.army.entries[0].profile is first_profile
    assert candidate.army.entries[1].profile is second_profile

def test_build_candidate_groups_repeated_profiles_into_quantity():
    profile = create_test_profile(
        "REPEATED",
        points=20,
    )

    candidate = build_candidate(
        (
            profile,
            profile,
        )
    )

    assert candidate.army.profile_count() == 1
    assert candidate.army.model_count() == 2
    assert candidate.army.total_points() == 40

    assert candidate.army.entries[0].profile is profile
    assert candidate.army.entries[0].quantity == 2

def test_enumerate_repeated_selections_allows_repeated_items():
    items = (
        "A",
        "B",
    )

    selections = enumerate_repeated_selections(
        items=items,
        selection_size=2,
    )

    assert selections == (
        ("A", "A"),
        ("A", "B"),
        ("B", "B"),
    )

def test_filter_legal_candidates_removes_armies_over_points_limit():
    cheap_first = create_test_profile(
        "CHEAP_FIRST",
        points=20,
    )

    cheap_second = create_test_profile(
        "CHEAP_SECOND",
        points=20,
    )

    expensive_first = create_test_profile(
        "EXPENSIVE_FIRST",
        points=60,
    )

    expensive_second = create_test_profile(
        "EXPENSIVE_SECOND",
        points=60,
    )

    legal_candidate = build_candidate(
        (
            cheap_first,
            cheap_second,
        )
    )

    illegal_candidate = build_candidate(
        (
            expensive_first,
            expensive_second,
        )
    )

    legal_candidates = filter_legal_candidates(
        candidates=(
            legal_candidate,
            illegal_candidate,
        ),
        points_limit=100,
    )

    assert legal_candidates == (
        legal_candidate,
    )

def test_filter_legal_candidates_removes_armies_exceeding_max_in_army():
    profile = create_test_profile(
        "LIMITED",
        points=20,
    )

    legal_candidate = build_candidate(
        (
            profile,
        )
    )

    illegal_candidate = build_candidate(
        (
            profile,
            profile,
        )
    )

    legal_candidates = filter_legal_candidates(
        candidates=(
            legal_candidate,
            illegal_candidate,
        ),
        points_limit=100,
    )

    assert legal_candidates == (
        legal_candidate,
    )

def test_enumerate_profile_quantities_respects_max_in_army():
    profile = create_test_profile(
        "LIMITED",
        points=80,
    )
    profile.max_in_army = 2

    quantities = enumerate_profile_quantities(
        profile=profile,
        points_limit=700,
    )

    assert quantities == (
        0,
        1,
        2,
    )

def test_enumerate_profile_quantities_respects_max_in_army():
    profile = create_test_profile(
        "LIMITED",
        points=80,
        max_in_army=2,
    )

    quantities = enumerate_profile_quantities(
        profile=profile,
        points_limit=700,
    )

    assert quantities == (
        0,
        1,
        2,
    )

def test_enumerate_profile_quantities_caps_unlimited_profile_by_points():
    profile = create_test_profile(
        "UNLIMITED",
        points=200,
        max_in_army=0,
    )

    quantities = enumerate_profile_quantities(
        profile=profile,
        points_limit=700,
    )

    assert quantities == (
        0,
        1,
        2,
        3,
    )

def test_enumerate_quantity_candidates_builds_all_non_empty_combinations():
    first = create_test_profile(
        "FIRST",
        points=20,
        max_in_army=1,
    )
    second = create_test_profile(
        "SECOND",
        points=30,
        max_in_army=2,
    )

    candidates = enumerate_quantity_candidates(
        profiles=(
            first,
            second,
        ),
        points_limit=100,
    )

    assert tuple(
        tuple(
            (entry.profile.id, entry.quantity)
            for entry in candidate.army.entries
        )
        for candidate in candidates
    ) == (
        (
            ("SECOND", 1),
        ),
        (
            ("SECOND", 2),
        ),
        (
            ("FIRST", 1),
        ),
        (
            ("FIRST", 1),
            ("SECOND", 1),
        ),
        (
            ("FIRST", 1),
            ("SECOND", 2),
        ),
    )

def test_enumerate_legal_quantity_candidates_filters_over_points_armies():
    first = create_test_profile(
        "FIRST",
        points=60,
        max_in_army=1,
    )
    second = create_test_profile(
        "SECOND",
        points=60,
        max_in_army=1,
    )

    candidates = enumerate_legal_quantity_candidates(
        profiles=(
            first,
            second,
        ),
        points_limit=100,
    )

    assert tuple(
        tuple(
            (entry.profile.id, entry.quantity)
            for entry in candidate.army.entries
        )
        for candidate in candidates
    ) == (
        (
            ("SECOND", 1),
        ),
        (
            ("FIRST", 1),
        ),
    )

def test_enumerate_legal_quantity_candidates_preserves_deterministic_order():
    first = create_test_profile(
        "FIRST",
        points=60,
        max_in_army=1,
    )
    second = create_test_profile(
        "SECOND",
        points=40,
        max_in_army=2,
    )

    candidates = enumerate_legal_quantity_candidates(
        profiles=(
            first,
            second,
        ),
        points_limit=100,
    )

    assert tuple(
        tuple(
            (entry.profile.id, entry.quantity)
            for entry in candidate.army.entries
        )
        for candidate in candidates
    ) == (
        (
            ("SECOND", 1),
        ),
        (
            ("SECOND", 2),
        ),
        (
            ("FIRST", 1),
        ),
        (
            ("FIRST", 1),
            ("SECOND", 1),
        ),
    )

def test_enumerate_legal_quantity_candidates_preserves_deterministic_order():
    first = create_test_profile(
        "FIRST",
        points=60,
        max_in_army=1,
    )
    second = create_test_profile(
        "SECOND",
        points=40,
        max_in_army=2,
    )

    candidates = enumerate_legal_quantity_candidates(
        profiles=(
            first,
            second,
        ),
        points_limit=100,
    )

    assert tuple(
        tuple(
            (entry.profile.id, entry.quantity)
            for entry in candidate.army.entries
        )
        for candidate in candidates
    ) == (
        (
            ("SECOND", 1),
        ),
        (
            ("SECOND", 2),
        ),
        (
            ("FIRST", 1),
        ),
        (
            ("FIRST", 1),
            ("SECOND", 1),
        ),
    )
from composition_resolver import (
    build_legal_multi_group_candidates,
    build_multi_group_candidates,
    build_single_group_candidates,
    enumerate_group_selections,
    resolve_fixed_profiles,
    resolve_selection_group,
)
from composition_spec import (
    CompositionSelectionGroup,
    CompositionSpec,
)
from loader import load_all_profiles


def test_resolve_fixed_profiles_returns_canonical_profiles_by_quantity():
    profiles = load_all_profiles()

    spec = CompositionSpec(
        fixed_profiles=(
            ("DG_NEC", 1),
        ),
    )

    resolved = resolve_fixed_profiles(
        spec=spec,
        profiles=profiles,
    )

    assert tuple(
        profile.id
        for profile in resolved
    ) == (
        "DG_NEC",
    )
def test_resolve_selection_group_returns_canonical_profile_pool():
    profiles = load_all_profiles()

    group = CompositionSelectionGroup(
        profile_ids=(
            "DG_WK",
            "DG_KHM",
            "DG_DH",
        ),
        selection_size=2,
    )

    resolved = resolve_selection_group(
        group=group,
        profiles=profiles,
    )

    assert tuple(
        profile.id
        for profile in resolved
    ) == (
        "DG_WK",
        "DG_KHM",
        "DG_DH",
    )

def test_enumerate_group_selections_generates_repeated_profile_combinations():
    profiles = load_all_profiles()

    group = CompositionSelectionGroup(
        profile_ids=(
            "DG_AK",
            "DG_SM",
        ),
        selection_size=2,
    )

    selections = enumerate_group_selections(
        group=group,
        profiles=profiles,
    )

    assert tuple(
        tuple(
            profile.id
            for profile in selection
        )
        for selection in selections
    ) == (
        ("DG_AK", "DG_AK"),
        ("DG_AK", "DG_SM"),
        ("DG_SM", "DG_SM"),
    )

def test_build_single_group_candidates_combines_fixed_and_selected_profiles():
    profiles = load_all_profiles()

    spec = CompositionSpec(
        fixed_profiles=(
            ("DG_NEC", 1),
        ),
        selection_groups=(
            CompositionSelectionGroup(
                profile_ids=(
                    "DG_AK",
                    "DG_SM",
                ),
                selection_size=2,
            ),
        ),
    )

    candidates = build_single_group_candidates(
        spec=spec,
        profiles=profiles,
    )

    assert tuple(
        tuple(
            (entry.profile.id, entry.quantity)
            for entry in candidate.army.entries
        )
        for candidate in candidates
    ) == (
        (
            ("DG_NEC", 1),
            ("DG_AK", 2),
        ),
        (
            ("DG_NEC", 1),
            ("DG_AK", 1),
            ("DG_SM", 1),
        ),
        (
            ("DG_NEC", 1),
            ("DG_SM", 2),
        ),
    )

def test_build_multi_group_candidates_combines_all_selection_groups():
    profiles = load_all_profiles()

    spec = CompositionSpec(
        fixed_profiles=(
            ("DG_NEC", 1),
        ),
        selection_groups=(
            CompositionSelectionGroup(
                profile_ids=(
                    "DG_AK",
                    "DG_SM",
                ),
                selection_size=1,
            ),
            CompositionSelectionGroup(
                profile_ids=(
                    "DG_MGS",
                    "DG_MHS",
                ),
                selection_size=1,
            ),
        ),
    )

    candidates = build_multi_group_candidates(
        spec=spec,
        profiles=profiles,
    )

    assert tuple(
        tuple(
            (entry.profile.id, entry.quantity)
            for entry in candidate.army.entries
        )
        for candidate in candidates
    ) == (
        (
            ("DG_NEC", 1),
            ("DG_AK", 1),
            ("DG_MGS", 1),
        ),
        (
            ("DG_NEC", 1),
            ("DG_AK", 1),
            ("DG_MHS", 1),
        ),
        (
            ("DG_NEC", 1),
            ("DG_SM", 1),
            ("DG_MGS", 1),
        ),
        (
            ("DG_NEC", 1),
            ("DG_SM", 1),
            ("DG_MHS", 1),
        ),
    )

def test_build_legal_multi_group_candidates_filters_illegal_armies():
    profiles = load_all_profiles()

    spec = CompositionSpec(
        fixed_profiles=(
            ("DG_NEC", 1),
        ),
        selection_groups=(
            CompositionSelectionGroup(
                profile_ids=(
                    "DG_WK",
                    "DG_AK",
                ),
                selection_size=2,
            ),
            CompositionSelectionGroup(
                profile_ids=(
                    "DG_MGS",
                ),
                selection_size=1,
            ),
        ),
    )

    candidates = build_legal_multi_group_candidates(
        spec=spec,
        profiles=profiles,
        points_limit=700,
    )

    assert tuple(
        tuple(
            (entry.profile.id, entry.quantity)
            for entry in candidate.army.entries
        )
        for candidate in candidates
    ) == (
        (
            ("DG_NEC", 1),
            ("DG_WK", 1),
            ("DG_AK", 1),
            ("DG_MGS", 1),
        ),
        (
            ("DG_NEC", 1),
            ("DG_AK", 2),
            ("DG_MGS", 1),
        ),
    )
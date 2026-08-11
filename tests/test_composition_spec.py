from composition_spec import (
    CompositionSelectionGroup,
    CompositionSpec,
)


def test_composition_spec_stores_fixed_profile_quantities():
    spec = CompositionSpec(
        fixed_profiles=(
            ("DG_NEC", 1),
        ),
    )

    assert spec.fixed_profiles == (
        ("DG_NEC", 1),
    )

def test_composition_selection_group_stores_profile_ids_and_selection_size():
    group = CompositionSelectionGroup(
        profile_ids=(
            "DG_WK",
            "DG_KHM",
            "DG_DH",
        ),
        selection_size=2,
    )

    assert group.profile_ids == (
        "DG_WK",
        "DG_KHM",
        "DG_DH",
    )

    assert group.selection_size == 2

def test_composition_spec_stores_selection_groups():
    nazgul_group = CompositionSelectionGroup(
        profile_ids=(
            "DG_WK",
            "DG_KHM",
        ),
        selection_size=1,
    )

    spec = CompositionSpec(
        fixed_profiles=(
            ("DG_NEC", 1),
        ),
        selection_groups=(
            nazgul_group,
        ),
    )

    assert spec.selection_groups == (
        nazgul_group,
    )
import pytest

from profile_swap import ProfileSwap


def test_profile_swap_stores_removed_and_added_profile_ids():
    swap = ProfileSwap(
        removed_profile_id="nazgul_a",
        added_profile_id="nazgul_b",
    )

    assert swap.removed_profile_id == "nazgul_a"
    assert swap.added_profile_id == "nazgul_b"


def test_profile_swap_is_immutable():
    swap = ProfileSwap(
        removed_profile_id="nazgul_a",
        added_profile_id="nazgul_b",
    )

    with pytest.raises(Exception):
        swap.removed_profile_id = "nazgul_c"


def test_profile_swap_rejects_same_profile_as_remove_and_add():
    with pytest.raises(ValueError):
        ProfileSwap(
            removed_profile_id="nazgul_a",
            added_profile_id="nazgul_a",
        )
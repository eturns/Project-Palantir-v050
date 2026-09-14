from army_loader import (
    load_army_list_profiles,
    load_army_lists,
    load_factions,
)
from loader import load_all_profiles
import pytest

def test_load_army_list_profiles_populates_canonical_memberships():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    factions = load_factions()

    army_lists = load_army_lists(
        factions,
    )

    load_army_list_profiles(
        army_lists=army_lists,
        profiles_by_id=profiles_by_id,
    )

    rise_of_the_necromancer = army_lists[
        "DG_ROTN"
    ]

    iron_hills = army_lists[
        "IH_IRON_HILLS"
    ]

    assert {
        profile.id
        for profile in rise_of_the_necromancer.profiles
    } == {
        "DG_NEC",
        "DG_WK",
        "DG_KHM",
        "DG_DH",
        "DG_FS",
        "DG_LS",
        "DG_AK",
        "DG_SM",
        "DG_MGS",
        "DG_MHS",
    }

    assert {
        profile.id
        for profile in iron_hills.profiles
    } == {
        "IH_WR",
        "IH_DAIN",
        "IH_CAP",
        "IH_GR",
        "IH_CHARIOT",
    }

    assert all(
        profile
        is profiles_by_id[profile.id]
        for army_list in army_lists.values()
        for profile in army_list.profiles
    )

def test_same_canonical_profile_can_belong_to_multiple_army_lists(
    tmp_path,
    monkeypatch,
):
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    factions = load_factions()

    army_lists = load_army_lists(
        factions,
    )

    membership_file = (
        tmp_path
        / "army_list_profiles.csv"
    )

    membership_file.write_text(
        "\n".join(
            (
                "army_list_id,profile_id",
                "DG_ROTN,DG_NEC",
                "IH_IRON_HILLS,DG_NEC",
            )
        ),
        encoding="utf-8",
    )

    original_open = open

    def patched_open(
        file,
        *args,
        **kwargs,
    ):
        if (
            str(file)
            == "data/factions/army_list_profiles.csv"
        ):
            return original_open(
                membership_file,
                *args,
                **kwargs,
            )

        return original_open(
            file,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        "builtins.open",
        patched_open,
    )

    load_army_list_profiles(
        army_lists=army_lists,
        profiles_by_id=profiles_by_id,
    )

    dg_profile = army_lists[
        "DG_ROTN"
    ].profiles[0]

    iron_hills_profile = army_lists[
        "IH_IRON_HILLS"
    ].profiles[0]

    assert dg_profile is profiles_by_id[
        "DG_NEC"
    ]

    assert iron_hills_profile is profiles_by_id[
        "DG_NEC"
    ]

    assert dg_profile is iron_hills_profile

def test_duplicate_army_list_profile_membership_is_rejected(
    tmp_path,
    monkeypatch,
):
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    factions = load_factions()

    army_lists = load_army_lists(
        factions,
    )

    membership_file = (
        tmp_path
        / "army_list_profiles.csv"
    )

    membership_file.write_text(
        "\n".join(
            (
                "army_list_id,profile_id",
                "DG_ROTN,DG_NEC",
                "DG_ROTN,DG_NEC",
            )
        ),
        encoding="utf-8",
    )

    original_open = open

    def patched_open(
        file,
        *args,
        **kwargs,
    ):
        if (
            str(file)
            == "data/factions/army_list_profiles.csv"
        ):
            return original_open(
                membership_file,
                *args,
                **kwargs,
            )

        return original_open(
            file,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        "builtins.open",
        patched_open,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Duplicate ArmyList profile membership: "
            "DG_ROTN / DG_NEC"
        ),
    ):
        load_army_list_profiles(
            army_lists=army_lists,
            profiles_by_id=profiles_by_id,
        )

def test_unknown_profile_in_army_list_membership_is_rejected(
    tmp_path,
    monkeypatch,
):
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    factions = load_factions()

    army_lists = load_army_lists(
        factions,
    )

    membership_file = (
        tmp_path
        / "army_list_profiles.csv"
    )

    membership_file.write_text(
        "\n".join(
            (
                "army_list_id,profile_id",
                "DG_ROTN,UNKNOWN_PROFILE",
            )
        ),
        encoding="utf-8",
    )

    original_open = open

    def patched_open(
        file,
        *args,
        **kwargs,
    ):
        if (
            str(file)
            == "data/factions/army_list_profiles.csv"
        ):
            return original_open(
                membership_file,
                *args,
                **kwargs,
            )

        return original_open(
            file,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        "builtins.open",
        patched_open,
    )

    with pytest.raises(
        ValueError,
    ):
        load_army_list_profiles(
            army_lists=army_lists,
            profiles_by_id=profiles_by_id,
        )

def test_unknown_army_list_in_profile_membership_is_rejected(
    tmp_path,
    monkeypatch,
):
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    factions = load_factions()

    army_lists = load_army_lists(
        factions,
    )

    membership_file = (
        tmp_path
        / "army_list_profiles.csv"
    )

    membership_file.write_text(
        "\n".join(
            (
                "army_list_id,profile_id",
                "UNKNOWN_LIST,DG_NEC",
            )
        ),
        encoding="utf-8",
    )

    original_open = open

    def patched_open(
        file,
        *args,
        **kwargs,
    ):
        if (
            str(file)
            == "data/factions/army_list_profiles.csv"
        ):
            return original_open(
                membership_file,
                *args,
                **kwargs,
            )

        return original_open(
            file,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        "builtins.open",
        patched_open,
    )

    with pytest.raises(
        ValueError,
    ):
        load_army_list_profiles(
            army_lists=army_lists,
            profiles_by_id=profiles_by_id,
        )
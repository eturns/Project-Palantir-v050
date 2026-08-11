from army_profile_resolver import resolve_army_profiles
from loader import load_all_profiles


def test_resolve_army_profiles_returns_complete_dol_guldur_pool():
    profiles = load_all_profiles()

    army_profiles = resolve_army_profiles(
        army="Dol Guldur",
        profiles=profiles,
    )

    assert tuple(
        profile.id
        for profile in army_profiles
    ) == (
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
    )
from dol_guldur_compositions import (
    dol_guldur_family_a_spec,
    dol_guldur_family_b_spec,
    dol_guldur_nazgul_profiles,
    dol_guldur_spider_profiles,
)
from composition_resolver import (
    build_legal_multi_group_candidates,
)
from loader import load_all_profiles

def test_dol_guldur_nazgul_profiles_returns_canonical_nazgul_pool():
    profiles = load_all_profiles()

    nazgul = dol_guldur_nazgul_profiles(
        profiles
    )

    assert tuple(
        profile.id
        for profile in nazgul
    ) == (
        "DG_WK",
        "DG_KHM",
        "DG_DH",
        "DG_FS",
        "DG_LS",
        "DG_AK",
        "DG_SM",
    )
def test_dol_guldur_spider_profiles_returns_canonical_spider_pool():
    profiles = load_all_profiles()

    spiders = dol_guldur_spider_profiles(
        profiles
    )

    assert tuple(
        profile.id
        for profile in spiders
    ) == (
        "DG_MGS",
        "DG_MHS",
    )

def test_dol_guldur_family_a_generates_all_legal_candidates():
    profiles = load_all_profiles()

    spec = dol_guldur_family_a_spec(
        profiles
    )

    candidates = build_legal_multi_group_candidates(
        spec=spec,
        profiles=profiles,
        points_limit=700,
    )

    assert len(candidates) == 94

    assert all(
        candidate.army.total_points() == 700
        for candidate in candidates
    )

    assert all(
        candidate.army.validate(700) == []
        for candidate in candidates
    )

def test_dol_guldur_family_b_generates_all_legal_candidates():
    profiles = load_all_profiles()

    spec = dol_guldur_family_b_spec(
        profiles
    )

    candidates = build_legal_multi_group_candidates(
        spec=spec,
        profiles=profiles,
        points_limit=700,
    )

    assert len(candidates) == 396

    assert all(
        candidate.army.total_points() == 700
        for candidate in candidates
    )

    assert all(
        candidate.army.validate(700) == []
        for candidate in candidates
    )
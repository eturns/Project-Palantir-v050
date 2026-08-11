from dol_guldur_compositions import (
    dol_guldur_family_a_spec,
    dol_guldur_family_b_spec,
)
from loader import load_all_profiles
from optimisation_request import (
    OptimisationGoal,
    OptimisationRequest,
)
from optimisation_request_resolver import (
    build_request_candidates,
)


def test_build_request_candidates_generates_family_a_candidates():
    profiles = load_all_profiles()

    request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.BALANCED,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles
        ),
    )

    candidates = build_request_candidates(
        request=request,
        profiles=profiles,
    )

    assert len(candidates) == 94


def test_build_request_candidates_generates_family_b_candidates():
    profiles = load_all_profiles()

    request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.BOARD_PRESENCE,
            OptimisationGoal.MAGIC,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles
        ),
    )

    candidates = build_request_candidates(
        request=request,
        profiles=profiles,
    )

    assert len(candidates) == 396

def test_build_request_candidates_generates_open_army_candidates():
    profiles = load_all_profiles()

    request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.BALANCED,
        ),
    )

    candidates = build_request_candidates(
        request=request,
        profiles=profiles,
    )

    assert len(candidates) > 0

    assert all(
        candidate.army.validate(700) == []
        for candidate in candidates
    )

def test_build_request_candidates_generates_complete_open_dol_guldur_population():
    profiles = load_all_profiles()

    request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.BALANCED,
        ),
    )

    candidates = build_request_candidates(
        request=request,
        profiles=profiles,
    )

    assert len(candidates) == 71346

    assert all(
        candidate.army.validate(700) == []
        for candidate in candidates
    )

def test_open_dol_guldur_candidates_are_deterministic_and_unique():
    profiles = load_all_profiles()

    request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.BALANCED,
        ),
    )

    first_run = build_request_candidates(
        request=request,
        profiles=profiles,
    )

    second_run = build_request_candidates(
        request=request,
        profiles=profiles,
    )

    first_signatures = tuple(
        tuple(
            (entry.profile.id, entry.quantity)
            for entry in candidate.army.entries
        )
        for candidate in first_run
    )

    second_signatures = tuple(
        tuple(
            (entry.profile.id, entry.quantity)
            for entry in candidate.army.entries
        )
        for candidate in second_run
    )

    assert first_signatures == second_signatures

    assert len(set(first_signatures)) == len(
        first_signatures
    )
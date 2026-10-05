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
from army_loader import (
    load_army_list_profiles,
    load_army_lists,
    load_factions,
)
from composition_spec import (
    CompositionSelectionGroup,
    CompositionSpec,
)
import pytest

def load_rise_of_the_necromancer_army_list(
    profiles,
):
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

    return army_lists["DG_ROTN"]


def test_build_request_candidates_generates_family_a_candidates():
    profiles = load_all_profiles()

    army_list = load_rise_of_the_necromancer_army_list(
        profiles
    )

    request = OptimisationRequest(
        army_list=army_list,
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
    )

    assert len(candidates) == 94

def test_open_ended_optimisation_is_rejected():
    profiles = load_all_profiles()

    army_list = load_rise_of_the_necromancer_army_list(
        profiles
    )

    request = OptimisationRequest(
        army_list=army_list,
        points_limit=700,
        goals=(
            OptimisationGoal.BALANCED,
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            "Open-ended army enumeration "
            "is not supported"
        ),
    ):
        build_request_candidates(
            request=request,
        )

def test_build_request_candidates_generates_family_b_candidates():
    profiles = load_all_profiles()

    army_list = load_rise_of_the_necromancer_army_list(
        profiles
    )

    request = OptimisationRequest(
        army_list=army_list,
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
    )

    assert len(candidates) == 396

def test_composition_spec_cannot_use_profile_outside_army_list():
    profiles = load_all_profiles()

    army_list = load_rise_of_the_necromancer_army_list(
        profiles
    )

    spec = CompositionSpec(
        fixed_profiles=(
            ("IH_DAIN", 1),
        ),
    )

    request = OptimisationRequest(
        army_list=army_list,
        points_limit=700,
        goals=(
            OptimisationGoal.BALANCED,
        ),
        composition_spec=spec,
    )

    with pytest.raises(
        KeyError,
    ):
        build_request_candidates(
            request=request,
        )

def test_selection_group_cannot_use_profile_outside_army_list():
    profiles = load_all_profiles()

    army_list = load_rise_of_the_necromancer_army_list(
        profiles
    )

    spec = CompositionSpec(
        selection_groups=(
            CompositionSelectionGroup(
                profile_ids=(
                    "DG_WK",
                    "IH_DAIN",
                ),
                selection_size=1,
            ),
        ),
    )

    request = OptimisationRequest(
        army_list=army_list,
        points_limit=700,
        goals=(
            OptimisationGoal.BALANCED,
        ),
        composition_spec=spec,
    )

    with pytest.raises(
        KeyError,
    ):
        build_request_candidates(
            request=request,
        )
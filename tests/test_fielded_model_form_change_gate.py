import pytest

from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
from fielded_model_form_state import FieldedModelFormState
from fielded_model_form_change_gate import (
    request_fielded_model_form_change,
)
from profiles import Profile


def make_profile(
    profile_id: str,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )


def test_rule_gate_rejects_form_change_when_not_currently_permitted():
    man_profile = make_profile("BEORN")
    bear_profile = make_profile("BEORN_THE_BEAR")

    fielded_model = FieldedModel(
        id="BEORN:1:1",
        configured_profile=ConfiguredProfile(
            profile=man_profile,
        ),
    )

    state = FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=(
            fielded_model.configured_profile
        ),
        allowed_alternate_profile_ids=frozenset(
            {
                "BEORN_THE_BEAR",
            }
        ),
    )

    with pytest.raises(
        ValueError,
        match="Form change is not currently permitted",
    ):
        request_fielded_model_form_change(
            state=state,
            new_active_configured_profile=(
                ConfiguredProfile(
                    profile=bear_profile,
                )
            ),
            transition_permitted=False,
        )

def test_rule_gate_delegates_form_change_when_permitted():
    man_profile = make_profile("BEORN")
    bear_profile = make_profile("BEORN_THE_BEAR")

    fielded_model = FieldedModel(
        id="BEORN:1:1",
        configured_profile=ConfiguredProfile(
            profile=man_profile,
        ),
    )

    state = FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=(
            fielded_model.configured_profile
        ),
        allowed_alternate_profile_ids=frozenset(
            {
                "BEORN_THE_BEAR",
            }
        ),
    )

    bear_state = request_fielded_model_form_change(
        state=state,
        new_active_configured_profile=(
            ConfiguredProfile(
                profile=bear_profile,
            )
        ),
        transition_permitted=True,
    )

    assert bear_state.fielded_model is fielded_model
    assert (
        bear_state.active_configured_profile.profile.id
        == "BEORN_THE_BEAR"
    )
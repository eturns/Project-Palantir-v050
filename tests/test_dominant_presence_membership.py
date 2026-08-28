import pytest

from dominant_presence import (
    are_required_dominant_presence_models_in_range,
    resolve_dominant_presence_override_from_model_ids,
)
from objective_control_override import (
    ObjectiveControlOverride,
)

def test_all_required_models_in_range_activates_membership_check():
    result = are_required_dominant_presence_models_in_range(
        required_model_ids={
            "BILL",
            "BERT",
            "TOM",
        },
        model_ids_in_range={
            "BILL",
            "BERT",
            "TOM",
        },
    )

    assert result is True


def test_missing_required_model_fails_membership_check():
    result = are_required_dominant_presence_models_in_range(
        required_model_ids={
            "BILL",
            "BERT",
            "TOM",
        },
        model_ids_in_range={
            "BILL",
            "BERT",
        },
    )

    assert result is False


def test_unrelated_model_does_not_replace_required_model():
    result = are_required_dominant_presence_models_in_range(
        required_model_ids={
            "BILL",
            "BERT",
            "TOM",
        },
        model_ids_in_range={
            "BILL",
            "BERT",
            "GOBLIN",
        },
    )

    assert result is False


def test_extra_models_do_not_prevent_activation():
    result = are_required_dominant_presence_models_in_range(
        required_model_ids={
            "BILL",
            "BERT",
            "TOM",
        },
        model_ids_in_range={
            "BILL",
            "BERT",
            "TOM",
            "GOBLIN",
        },
    )

    assert result is True


def test_required_model_ids_cannot_be_empty():
    with pytest.raises(ValueError):
        are_required_dominant_presence_models_in_range(
            required_model_ids=set(),
            model_ids_in_range={
                "BILL",
            },
        )


def test_model_id_inputs_must_be_sets():
    with pytest.raises(TypeError):
        are_required_dominant_presence_models_in_range(
            required_model_ids=[
                "BILL",
                "BERT",
                "TOM",
            ],
            model_ids_in_range={
                "BILL",
                "BERT",
                "TOM",
            },
        )

def test_model_id_resolver_returns_automatic_control_when_required_group_is_present():
    result = resolve_dominant_presence_override_from_model_ids(
        required_model_ids={
            "BILL",
            "BERT",
            "TOM",
        },
        model_ids_in_range={
            "BILL",
            "BERT",
            "TOM",
        },
    )

    assert result == ObjectiveControlOverride.AUTOMATIC_CONTROL


def test_model_id_resolver_returns_no_override_when_required_group_is_incomplete():
    result = resolve_dominant_presence_override_from_model_ids(
        required_model_ids={
            "BILL",
            "BERT",
            "TOM",
        },
        model_ids_in_range={
            "BILL",
            "BERT",
            "GOBLIN",
        },
    )

    assert result == ObjectiveControlOverride.NONE
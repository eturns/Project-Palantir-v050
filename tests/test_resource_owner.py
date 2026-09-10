import pytest

from resource_owner import ResourceOwner


def test_resource_owner_stores_fielded_model_id():
    owner = ResourceOwner(
        fielded_model_id="DG_SM:1:1",
    )

    assert owner.fielded_model_id == "DG_SM:1:1"


def test_resource_owner_distinguishes_fielded_models():
    first_owner = ResourceOwner(
        fielded_model_id="DG_SM:1:1",
    )

    second_owner = ResourceOwner(
        fielded_model_id="DG_SM:1:2",
    )

    assert first_owner != second_owner


def test_equivalent_resource_owners_are_equal():
    first_owner = ResourceOwner(
        fielded_model_id="DG_SM:1:1",
    )

    second_owner = ResourceOwner(
        fielded_model_id="DG_SM:1:1",
    )

    assert first_owner == second_owner


def test_resource_owner_key_is_fielded_model_id():
    owner = ResourceOwner(
        fielded_model_id="DG_SM:2:1",
    )

    assert owner.key == "DG_SM:2:1"


def test_resource_owner_rejects_empty_fielded_model_id():
    with pytest.raises(
        ValueError,
        match="fielded model id must not be empty",
    ):
        ResourceOwner(
            fielded_model_id="",
        )
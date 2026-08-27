import pytest
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from scenario_presence import (
    calculate_army_scenario_presence,
    calculate_dominant_presence_weight,
    calculate_model_scenario_presence,
    calculate_profile_scenario_presence,
    calculate_scenario_presence_weight,
    calculate_total_model_scenario_presence,
    calculate_total_scenario_presence,
)


def test_standard_model_counts_as_one():
    assert (
        calculate_scenario_presence_weight(
            dominant_value=None,
        )
        == 1
    )


def test_dominant_one_counts_as_one():
    assert (
        calculate_scenario_presence_weight(
            dominant_value=1,
        )
        == 1
    )


def test_dominant_three_counts_as_three():
    assert (
        calculate_scenario_presence_weight(
            dominant_value=3,
        )
        == 3
    )


def test_dominant_value_must_be_integer():
    with pytest.raises(
        TypeError,
        match="dominant_value must be an int or None.",
    ):
        calculate_scenario_presence_weight(
            dominant_value=3.0,
        )


def test_dominant_value_rejects_boolean():
    with pytest.raises(
        TypeError,
        match="dominant_value must be an int or None.",
    ):
        calculate_scenario_presence_weight(
            dominant_value=True,
        )


def test_dominant_value_cannot_be_less_than_one():
    with pytest.raises(
        ValueError,
        match="dominant_value must be at least 1.",
    ):
        calculate_scenario_presence_weight(
            dominant_value=0,
        )

def test_multiple_dominant_sources_use_highest_value():
    assert (
        calculate_dominant_presence_weight(
            dominant_values=(2, 4, 3),
        )
        == 4
    )


def test_no_dominant_sources_count_as_one():
    assert (
        calculate_dominant_presence_weight(
            dominant_values=(),
        )
        == 1
    )


def test_single_dominant_source_uses_that_value():
    assert (
        calculate_dominant_presence_weight(
            dominant_values=(3,),
        )
        == 3
    )


def test_dominant_sources_reject_invalid_entry():
    with pytest.raises(
        TypeError,
        match="dominant_values must contain only ints.",
    ):
        calculate_dominant_presence_weight(
            dominant_values=(2, "3"),
        )


def test_dominant_sources_reject_boolean_entry():
    with pytest.raises(
        TypeError,
        match="dominant_values must contain only ints.",
    ):
        calculate_dominant_presence_weight(
            dominant_values=(2, True),
        )


def test_dominant_sources_reject_value_below_one():
    with pytest.raises(
        ValueError,
        match="dominant_values must contain values of at least 1.",
    ):
        calculate_dominant_presence_weight(
            dominant_values=(2, 0),
        )

def test_total_scenario_presence_sums_standard_models():
    assert (
        calculate_total_scenario_presence(
            presence_weights=(1, 1, 1, 1),
        )
        == 4
    )


def test_total_scenario_presence_includes_dominant_weight():
    assert (
        calculate_total_scenario_presence(
            presence_weights=(1, 1, 3, 1),
        )
        == 6
    )


def test_total_scenario_presence_allows_empty_collection():
    assert (
        calculate_total_scenario_presence(
            presence_weights=(),
        )
        == 0
    )


def test_total_scenario_presence_rejects_non_integer_entry():
    with pytest.raises(
        TypeError,
        match="presence_weights must contain only ints.",
    ):
        calculate_total_scenario_presence(
            presence_weights=(1, 2.0),
        )


def test_total_scenario_presence_rejects_boolean_entry():
    with pytest.raises(
        TypeError,
        match="presence_weights must contain only ints.",
    ):
        calculate_total_scenario_presence(
            presence_weights=(1, True),
        )


def test_total_scenario_presence_rejects_value_below_one():
    with pytest.raises(
        ValueError,
        match="presence_weights must contain values of at least 1.",
    ):
        calculate_total_scenario_presence(
            presence_weights=(1, 0),
        )

def test_model_scenario_presence_defaults_to_one_without_dominant():
    assert (
        calculate_model_scenario_presence(
            dominant_values=(),
        )
        == 1
    )


def test_model_scenario_presence_uses_highest_dominant_source():
    assert (
        calculate_model_scenario_presence(
            dominant_values=(2, 4, 3),
        )
        == 4
    )


def test_model_scenario_presence_rejects_invalid_dominant_source():
    with pytest.raises(
        TypeError,
        match="dominant_values must contain only ints.",
    ):
        calculate_model_scenario_presence(
            dominant_values=(2, "4"),
        )

def test_total_model_scenario_presence_counts_standard_models():
    assert (
        calculate_total_model_scenario_presence(
            model_dominant_values=(
                (),
                (),
                (),
            ),
        )
        == 3
    )


def test_total_model_scenario_presence_includes_dominant_models():
    assert (
        calculate_total_model_scenario_presence(
            model_dominant_values=(
                (),
                (3,),
                (),
            ),
        )
        == 5
    )


def test_total_model_scenario_presence_uses_highest_dominant_per_model():
    assert (
        calculate_total_model_scenario_presence(
            model_dominant_values=(
                (2, 4),
                (3,),
            ),
        )
        == 7
    )


def test_total_model_scenario_presence_allows_no_models():
    assert (
        calculate_total_model_scenario_presence(
            model_dominant_values=(),
        )
        == 0
    )


def test_total_model_scenario_presence_rejects_invalid_model_entry():
    with pytest.raises(
        TypeError,
        match="model_dominant_values must contain only tuples.",
    ):
        calculate_total_model_scenario_presence(
            model_dominant_values=(
                (),
                3,
            ),
        )

def _load_profiles_with_special_rules():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    special_rules = load_special_rules()

    load_profile_special_rules(
        profiles_by_id,
        special_rules,
    )

    return profiles_by_id


def test_necromancer_real_profile_has_scenario_presence_five():
    profiles = _load_profiles_with_special_rules()

    result = calculate_profile_scenario_presence(
        profile=profiles["DG_NEC"],
    )

    assert result == 5


def test_witch_king_real_profile_has_scenario_presence_two():
    profiles = _load_profiles_with_special_rules()

    result = calculate_profile_scenario_presence(
        profile=profiles["DG_WK"],
    )

    assert result == 2


def test_spider_real_profile_defaults_to_scenario_presence_one():
    profiles = _load_profiles_with_special_rules()

    result = calculate_profile_scenario_presence(
        profile=profiles["DG_MGS"],
    )

    assert result == 1

def test_real_dol_guldur_core_has_scenario_presence_seventeen():
    profiles = _load_profiles_with_special_rules()

    army_profiles = (
        profiles["DG_NEC"],
        profiles["DG_WK"],
        profiles["DG_KHM"],
        profiles["DG_DH"],
        profiles["DG_FS"],
        profiles["DG_LS"],
        profiles["DG_AK"],
    )

    result = calculate_army_scenario_presence(
        profiles=army_profiles,
    )

    assert result == 17
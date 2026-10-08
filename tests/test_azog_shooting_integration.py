from tests.test_azogs_hunters_json_import_integration import (
    load_production_azogs_hunters_data,
)
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from army_shooting_capability import (
    resolve_army_ranged_shooters,
)
from army_shooting_capability import (
    calculate_army_shooting_output_density,
    resolve_army_ranged_shooters,
)
import pytest
from configured_profile import ConfiguredProfile
from fractions import Fraction
from objective_normalisation import (
    normalise_shooting_output_density,
)
from objective_normalisation import (
    normalise_shooting_output_density,
)

from projection_capability import (
    build_shooting_benchmark_defender,
)

def test_azog_shooting_fixture_identifies_all_orc_bow_models():
    (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    ) = load_production_azogs_hunters_data()

    _, army, _ = import_army_from_mesbg_list_builder(
        "tests/fixtures/azog_shooting_test.json",
        profiles_by_id=profiles_by_id,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=(
            options_by_external_id
        ),
    )

    bow_models = sum(
        entry.quantity
        for entry in army.entries
        if (
            entry.counts_as_model
            and any(
                item.id == "WG_ORC_BOW"
                for item
                in entry.configured_profile.effective_wargear
            )
        )
    )

    assert bow_models == 9

def test_azog_shooting_fixture_resolves_nine_ranged_shooters():
    (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    ) = load_production_azogs_hunters_data()

    _, army, _ = import_army_from_mesbg_list_builder(
        "tests/fixtures/azog_shooting_test.json",
        profiles_by_id=profiles_by_id,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=(
            options_by_external_id
        ),
    )

    shooters = resolve_army_ranged_shooters(
        army
    )

    assert len(shooters) == 9

    assert {
        weapon.wargear_id
        for _, weapon in shooters
    } == {
        "WG_ORC_BOW",
    }

def test_azog_shooting_fixture_calculates_real_output_density():
    (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    ) = load_production_azogs_hunters_data()

    _, army, _ = import_army_from_mesbg_list_builder(
        "tests/fixtures/azog_shooting_test.json",
        profiles_by_id=profiles_by_id,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=(
            options_by_external_id
        ),
    )

    defender = ConfiguredProfile(
        profile=profiles_by_id["DG_HOC"],
    )

    result = calculate_army_shooting_output_density(
        army=army,
        defender=defender,
    )

    assert result == Fraction(
        2500,
        18819,
    )

def test_azog_shooting_fixture_normalises_to_expected_score():
    (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    ) = load_production_azogs_hunters_data()

    _, army, _ = import_army_from_mesbg_list_builder(
        "tests/fixtures/azog_shooting_test.json",
        profiles_by_id=profiles_by_id,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=(
            options_by_external_id
        ),
    )

    defender = ConfiguredProfile(
        profile=profiles_by_id["DG_HOC"],
    )

    density = calculate_army_shooting_output_density(
        army=army,
        defender=defender,
    )

    result = normalise_shooting_output_density(
        density,
    )

    assert result == pytest.approx(
        12500 / 56457
    )

def test_azog_shooting_fixture_has_expected_benchmark_score():
    (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    ) = load_production_azogs_hunters_data()

    _, army, _ = import_army_from_mesbg_list_builder(
        "tests/fixtures/azog_shooting_test.json",
        profiles_by_id=profiles_by_id,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=(
            options_by_external_id
        ),
    )

    density = calculate_army_shooting_output_density(
        army=army,
        defender=build_shooting_benchmark_defender(),
    )

    score = normalise_shooting_output_density(
        density,
    )

    assert score == pytest.approx(
        12500 / 56457
    )
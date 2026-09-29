from types import SimpleNamespace

from evidence_status import EvidenceStatus
from metric_evidence import assess_ranged_wargear_evidence
from metric_evidence import assess_attrition_evidence
from pathlib import Path

from loader import load_all_profiles
from profile_option_loader import (
    load_profile_options,
    build_profile_options_by_external_id,
)
from profile_option_wargear_loader import (
    load_profile_option_wargear_assignments,
)
from wargear_loader import load_wargear
from army_loader import load_factions, load_army_lists
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)

def configured_profile_with_wargear(*wargear_ids):
    return SimpleNamespace(
        effective_wargear=tuple(
            SimpleNamespace(id=wargear_id)
            for wargear_id in wargear_ids
        ),
    )


def test_equipped_crossbow_has_provisional_evidence():
    evidence = assess_ranged_wargear_evidence(
        configured_profiles=(
            configured_profile_with_wargear(
                "WG_CROSSBOW",
            ),
        ),
    )

    assert evidence is not None
    assert evidence.mechanic == "ranged_wargear_weighting"
    assert evidence.status is EvidenceStatus.PROVISIONAL
    assert "damage" in evidence.reason.lower()


def test_army_without_ranged_wargear_has_no_warning():
    evidence = assess_ranged_wargear_evidence(
        configured_profiles=(
            configured_profile_with_wargear(),
        ),
    )

    assert evidence is None

def test_attrition_metric_is_provisional():
    evidence = assess_attrition_evidence()

    assert evidence.mechanic == "attrition_output"
    assert evidence.status is EvidenceStatus.PROVISIONAL
    assert evidence.provenance == "dev073_calibration"
    assert "casualty" in evidence.reason.lower()

def test_real_iron_hills_crossbows_have_provisional_evidence():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    options = load_profile_options(
        profiles=profiles,
    )

    load_profile_option_wargear_assignments(
        options,
        load_wargear(),
    )

    definition, army, army_list = (
        import_army_from_mesbg_list_builder(
            str(
                Path("tests")
                / "fixtures"
                / "iron_hills_army.json"
            ),
            profiles_by_id=profiles,
            army_lists_by_id=load_army_lists(
                load_factions()
            ),
            profile_options_by_external_id=(
                build_profile_options_by_external_id(
                    options
                )
            ),
        )
    )

    configured_profiles = tuple(
        model.configured_profile
        for model in army.fielded_models()
        if model.configured_profile is not None
    )

    evidence = assess_ranged_wargear_evidence(
        configured_profiles=configured_profiles,
    )

    assert evidence is not None
    assert evidence.mechanic == "ranged_wargear_weighting"
    assert evidence.status is EvidenceStatus.PROVISIONAL
from loader import load_profile
from profile_option_loader import (
    load_profile_options,
    build_profile_options_by_external_id,
)
from profile_option_state_effect_loader import (
    load_profile_option_state_effects,
)
from configured_profile import ConfiguredProfile
from profile_classification import HeroicStatus
from loader import load_all_profiles


def test_dale_siege_crew_matches_canonical_profile():
    crew = load_profile(
        "DALE_SIEGE_CREW"
    )

    assert crew.points == 0
    assert crew.movement == 6
    assert crew.fight == 4
    assert crew.shooting == "4+"
    assert crew.strength == 3
    assert crew.defence == 4
    assert crew.attacks == 1
    assert crew.wounds == 1
    assert crew.courage == "7+"
    assert crew.intelligence == "7+"
    assert crew.heroic_status is (
        HeroicStatus.WARRIOR
    )


def test_dale_siege_veteran_uses_configured_state():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    options = load_profile_options(
        profiles,
    )

    load_profile_option_state_effects(
        options,
    )

    options_by_external_id = (
        build_profile_options_by_external_id(
            options
        )
    )

    veteran_option = (
        options_by_external_id[
            "DALE_SIEGE_VETERAN"
        ]
    )

    crew = profiles[
        "DALE_SIEGE_CREW"
    ]

    configured = ConfiguredProfile(
        profile=crew,
        selected_options=(
            veteran_option,
        ),
    )

    assert configured.effective_heroic_status is (
        HeroicStatus.HERO
    )
    assert configured.effective_might == 1
    assert configured.effective_will == 1
    assert configured.effective_fate == 1

    assert crew.heroic_status is (
        HeroicStatus.WARRIOR
    )
    assert crew.might == 0
    assert crew.will == 0
    assert crew.fate == 0
from cavalry_knock_to_ground import (
    can_be_knocked_to_ground,
    cavalry_charge_knocks_down,
)
from combat_context import (
    CombatContext,
    EngagementRole,
)
from configured_profile import ConfiguredProfile
from mount import Mount
from profile_classification import ModelType
from profiles import Profile


def make_profile(
    *,
    profile_id: str,
    strength: int = 4,
    model_types: set[ModelType] | None = None,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=10,
        movement=6,
        fight=3,
        shooting="4+",
        strength=strength,
        defence=4,
        attacks=1,
        wounds=1,
        courage="8+",
        intelligence="8+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types=(
            model_types
            if model_types is not None
            else {
                ModelType.INFANTRY,
            }
        ),
    )


def make_cavalry_attacker() -> ConfiguredProfile:
    profile = make_profile(
        profile_id="ATTACKER",
        model_types={
            ModelType.CAVALRY,
        },
    )

    profile.default_mount = Mount(
        id="MOUNT_TEST",
        name="Test Mount",
        movement=10,
        fight=3,
        shooting="6+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="8+",
        intelligence="8+",
        base_size_mm=40,
    )

    return ConfiguredProfile(
        profile=profile,
    )


def make_eligible_context() -> CombatContext:
    return CombatContext(
        engagement_role=EngagementRole.CHARGED,
        charged_only_infantry=True,
        resolving_exclusively_against_infantry=True,
    )


def test_eligible_infantry_is_knocked_down_when_attacker_wins():
    attacker = make_cavalry_attacker()

    defender = ConfiguredProfile(
        profile=make_profile(
            profile_id="DEFENDER",
        ),
    )

    assert cavalry_charge_knocks_down(
        attacker,
        defender,
        make_eligible_context(),
        attacker_won_duel=True,
    ) is True


def test_defender_is_not_knocked_down_when_attacker_loses():
    attacker = make_cavalry_attacker()

    defender = ConfiguredProfile(
        profile=make_profile(
            profile_id="DEFENDER",
        ),
    )

    assert cavalry_charge_knocks_down(
        attacker,
        defender,
        make_eligible_context(),
        attacker_won_duel=False,
    ) is False


def test_monster_infantry_cannot_be_knocked_down():
    defender = ConfiguredProfile(
        profile=make_profile(
            profile_id="MONSTER",
            model_types={
                ModelType.INFANTRY,
                ModelType.MONSTER,
            },
        ),
    )

    assert can_be_knocked_to_ground(
        defender
    ) is False


def test_strength_six_infantry_cannot_be_knocked_down():
    defender = ConfiguredProfile(
        profile=make_profile(
            profile_id="STRONG_INFANTRY",
            strength=6,
        ),
    )

    assert can_be_knocked_to_ground(
        defender
    ) is False


def test_cavalry_defender_cannot_be_knocked_down():
    defender = ConfiguredProfile(
        profile=make_profile(
            profile_id="CAVALRY_DEFENDER",
            model_types={
                ModelType.CAVALRY,
            },
        ),
    )

    assert can_be_knocked_to_ground(
        defender
    ) is False


def test_invalid_cavalry_charge_does_not_knock_down():
    attacker = make_cavalry_attacker()

    defender = ConfiguredProfile(
        profile=make_profile(
            profile_id="DEFENDER",
        ),
    )

    context = CombatContext(
        engagement_role=EngagementRole.CHARGED,
        charged_only_infantry=True,
        resolving_exclusively_against_infantry=False,
    )

    assert cavalry_charge_knocks_down(
        attacker,
        defender,
        context,
        attacker_won_duel=True,
    ) is False
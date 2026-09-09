from battlefield_evidence import BattlefieldEvidence
from profiles import Profile
from ability_availability import ability_is_available
from configured_profile import ConfiguredProfile

def build_profile_battlefield_evidence(
    profile: Profile | ConfiguredProfile,
) -> BattlefieldEvidence:
    """
    Builds battlefield evidence for either a base Profile
    or one statically configured Profile.

    ConfiguredProfile is authoritative for analysis-relevant
    static state while the underlying Profile remains the
    source of intrinsic abilities not altered by configuration.
    """

    if isinstance(
        profile,
        ConfiguredProfile,
    ):
        base_profile = profile.profile
        special_rules = (
            profile.effective_special_rules
        )
    else:
        configured_profile = None
        base_profile = profile
        special_rules = profile.special_rules

    evidence = BattlefieldEvidence()

    # Special Rules
    for assignment in special_rules:

        if ability_is_available(
            base_profile,
            assignment.rule,
        ):
            evidence.available_special_rules.append(
                assignment,
            )

    # Heroic Actions
    for heroic_action in base_profile.heroic_actions:

        if ability_is_available(
            base_profile,
            heroic_action,
        ):
            evidence.available_heroic_actions.append(
                heroic_action,
            )

    # Spells
    for assignment in base_profile.spells:

        if ability_is_available(
            base_profile,
            assignment.spell,
        ):
            evidence.available_spells.append(
                assignment,
            )

    return evidence
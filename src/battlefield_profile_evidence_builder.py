from battlefield_evidence import BattlefieldEvidence
from profiles import Profile
from ability_availability import ability_is_available


def build_profile_battlefield_evidence(
    profile: Profile,
) -> BattlefieldEvidence:
    """
    Builds the battlefield evidence for a single Profile.
    """

    evidence = BattlefieldEvidence()

    # Special Rules
    for assignment in profile.special_rules:

        if ability_is_available(
            profile,
            assignment.rule,
        ):
            evidence.available_special_rules.append(
                assignment,
            )

    # Heroic Actions
    for heroic_action in profile.heroic_actions:

        if ability_is_available(
            profile,
            heroic_action,
        ):
            evidence.available_heroic_actions.append(
                heroic_action,
            )

    # Spells
    for assignment in profile.spells:

        if ability_is_available(
            profile,
            assignment.spell,
        ):
            evidence.available_spells.append(
                assignment,
            )

    return evidence
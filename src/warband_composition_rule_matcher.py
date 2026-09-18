from profiles import Profile
from warband_composition_rule import (
    WarbandCompositionRule,
)

def warband_composition_rule_applies_to_member(
    rule: WarbandCompositionRule,
    member: Profile,
    member_factions: tuple[str, ...] = (),
) -> bool:
    member_matches = True

    if rule.member_keywords:
        member_matches = (
            member_matches
            and any(
                keyword in member.keywords
                for keyword in rule.member_keywords
            )
        )

    if rule.member_races:
        member_matches = (
            member_matches
            and bool(member.races)
            and any(
                race in member.races
                for race in rule.member_races
            )
        )

    if rule.member_factions:
        member_matches = (
            member_matches
            and any(
                faction in member_factions
                for faction in rule.member_factions
            )
        )

    if rule.member_heroic_statuses:
        member_matches = (
            member_matches
            and member.heroic_status
            in rule.member_heroic_statuses
        )

    return member_matches

def warband_composition_rule_allows(
    rule: WarbandCompositionRule,
    member: Profile,
    leader: Profile,
    member_factions: tuple[str, ...] = (),
    leader_factions: tuple[str, ...] = (),
) -> bool:
    member_matches = True

    if rule.member_keywords:
        member_matches = (
            member_matches
            and any(
                keyword in member.keywords
                for keyword in rule.member_keywords
            )
        )

    if not warband_composition_rule_applies_to_member(
        rule,
        member,
        member_factions=member_factions,
    ):
        return True

    if not member_matches:
        return True

    if leader.id in rule.allowed_leader_profile_ids:
        return True

    leader_matches = True

    if rule.required_leader_keywords:
        leader_matches = (
            leader_matches
            and any(
                keyword in leader.keywords
                for keyword
                in rule.required_leader_keywords
            )
        )

    if rule.required_leader_races:
        leader_matches = (
            leader_matches
            and any(
                race in leader.races
                for race in rule.required_leader_races
            )
        )

    if rule.required_leader_factions:
        leader_matches = (
            leader_matches
            and any(
                faction in leader_factions
                for faction in rule.required_leader_factions
            )
        )

    if rule.required_leader_heroic_statuses:
        leader_matches = (
            leader_matches
            and leader.heroic_status
            in rule.required_leader_heroic_statuses
        )

    return leader_matches

    return False
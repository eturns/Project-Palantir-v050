from configured_profile import ConfiguredProfile


AUTOMATONS_RULE_ID = "AUTOMATONS"


def can_provide_stand_fast(
    configured_profile: ConfiguredProfile,
) -> bool:
    """
    Returns whether this model is permitted to provide
    a Stand Fast to nearby Warrior models.

    This represents rule eligibility only. Broken Army
    Courage Tests, range and Line of Sight are resolved
    by the wider Stand Fast system.
    """

    rule_ids = {
        assignment.rule.id
        for assignment
        in configured_profile.effective_special_rules
    }

    return AUTOMATONS_RULE_ID not in rule_ids
from army_rule import ArmyRule
from army_rule_metrics import ArmyRuleMetrics
from ability_queries import calculate_tag_score

def _calculate_tag(
    army_rule: ArmyRule,
    tag_id: str,
) -> float:

    return calculate_tag_score(
        [army_rule],
        tag_id,
    )

def calculate_army_rule_metrics(
    army_rule: ArmyRule,
) -> ArmyRuleMetrics:
    """
    Calculates the battlefield metric contribution of an Army Rule.
    """

    return ArmyRuleMetrics(
        offence=_calculate_tag(
            army_rule,
            "OFFENCE",
        ),
        defence=_calculate_tag(
            army_rule,
            "DEFENCE",
        ),
        mobility=_calculate_tag(
            army_rule,
            "MOBILITY",
        ),
        magic=_calculate_tag(
            army_rule,
            "MAGIC",
        ),
        shooting=_calculate_tag(
            army_rule,
            "SHOOTING",
        ),
        courage=_calculate_tag(
            army_rule,
            "COURAGE",
        ),
        control=_calculate_tag(
            army_rule,
            "CONTROL",
        ),
        command=_calculate_tag(
            army_rule,
            "COMMAND",
        ),
        objective=_calculate_tag(
        army_rule,
            "OBJECTIVE",
        ),
        hero_hunting=_calculate_tag(
            army_rule,
            "HERO_HUNTING",
        ),
    )
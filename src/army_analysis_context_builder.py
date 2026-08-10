from army import Army
from army_list import ArmyList
from army_analysis_context import ArmyAnalysisContext


def build_army_analysis_context(
    army: Army,
    army_list: ArmyList,
) -> ArmyAnalysisContext:
    """
    Builds temporary analysis modifiers from the active
    army list and its army rules.
    """

    context = ArmyAnalysisContext()

    for army_rule in army_list.army_rules:
        if army_rule.id == "DG_HIS_SPIRIT":
            context.extra_casting_dice_by_profile_id[
                "DG_NEC"
            ] = 1
        if army_rule.id == "DG_POWER_OF_THE_NECROMANCER":
            context.extra_spell_casts_by_profile_id[
                "DG_NEC"
        ] = 1    
    return context
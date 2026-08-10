from dataclasses import dataclass, field


@dataclass
class ArmyAnalysisContext:
    """
    Temporary modifiers created by the active army list
    during army analysis.
    """

    extra_casting_dice_by_profile_id: dict[str, int] = field(
        default_factory=dict,
    )
    extra_spell_casts_by_profile_id: dict[str, int] = field(
        default_factory=dict,
    )
"""DEV-077S-I2-G2-D3: explicit spell-outcome evidence contracts.

Spell catalogue categories and ability tags are heuristic metadata, not
mechanical evidence of wounds, kills or disabling. No scoring changes.
"""
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction


class SpellOutcomeKind(str, Enum):
    DIRECT_WOUNDS = "direct_wounds"
    REMOVE_TARGET = "remove_target"
    HERO_CONTROL = "hero_control"


@dataclass(frozen=True)
class VerifiedSpellOutcome:
    spell_id: str
    kind: SpellOutcomeKind
    rule_source: str
    wounds_on_effect: int | None = None
    controls_target: bool | None = None

    def __post_init__(self):
        if not self.spell_id.strip() or not self.rule_source.strip():
            raise ValueError("Verified spell outcome requires spell ID and rule source")
        if self.kind is SpellOutcomeKind.DIRECT_WOUNDS:
            if (isinstance(self.wounds_on_effect, bool) or
                    not isinstance(self.wounds_on_effect, int) or self.wounds_on_effect < 1):
                raise ValueError("Direct-wound spell requires positive integer wounds")
            if self.controls_target is not None:
                raise ValueError("Direct-wound spell cannot imply hero control")
        elif self.kind is SpellOutcomeKind.HERO_CONTROL:
            if self.controls_target is not True or self.wounds_on_effect is not None:
                raise ValueError("Hero-control effect must be explicitly confirmed")
        elif self.kind is SpellOutcomeKind.REMOVE_TARGET:
            if self.wounds_on_effect is not None or self.controls_target is not None:
                raise ValueError("Target removal must not imply wounds or control")
        else:
            raise ValueError("Unknown spell outcome type")


@dataclass(frozen=True)
class SpellHeroHuntingResult:
    spell_id: str
    spell_effect_probability: Fraction
    conditional_wounds: int | None
    direct_elimination_probability: Fraction | None
    conditional_hero_control_probability: Fraction | None
    evidence_status: str = "declared_rule_effect_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def calculate_declared_spell_hero_hunting(
    *, outcome: VerifiedSpellOutcome | None,
    effect_probability: Fraction,
    remaining_wounds: int,
    defensive_prevention_resolved: bool = False,
) -> SpellHeroHuntingResult:
    """Combine a verified external effect declaration with existing cast+resist.

    No outcome declarations are bundled: the user/project must verify actual
    spell wording, target legality, and defensive/prevention interactions.
    """
    if outcome is None:
        raise ValueError("Incomplete Hero Hunting: spell outcome not mechanically verified")
    if not isinstance(effect_probability, Fraction) or not 0 <= effect_probability <= 1:
        raise ValueError("effect_probability must be a Fraction in [0, 1]")
    if isinstance(remaining_wounds, bool) or not isinstance(remaining_wounds, int) or remaining_wounds < 1:
        raise ValueError("remaining_wounds must be a positive integer")
    if outcome.kind is SpellOutcomeKind.HERO_CONTROL:
        return SpellHeroHuntingResult(
            spell_id=outcome.spell_id, spell_effect_probability=effect_probability,
            conditional_wounds=None, direct_elimination_probability=None,
            conditional_hero_control_probability=effect_probability,
        )
    if not defensive_prevention_resolved:
        raise ValueError(
            "Incomplete Hero Hunting: magical elimination requires verified defensive/prevention context"
        )
    return SpellHeroHuntingResult(
        spell_id=outcome.spell_id, spell_effect_probability=effect_probability,
        conditional_wounds=outcome.wounds_on_effect,
        direct_elimination_probability=(
            effect_probability if (outcome.kind is SpellOutcomeKind.REMOVE_TARGET or
                                   outcome.wounds_on_effect >= remaining_wounds)
            else Fraction(0)
        ),
        conditional_hero_control_probability=None,
    )

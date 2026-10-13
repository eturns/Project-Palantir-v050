"""DEV-077S-I2-F2-A2: profile-level, diagnostic-only casting options.

Only a hypothetical single casting attempt is represented. The army-list
modifier is shown as a conditional option, not a prediction that its timing,
target or other prerequisites have been met. Legacy scoring is untouched.
"""
from dataclasses import dataclass

from army_analysis_context_builder import build_army_analysis_context
from battlefield_profile_evidence_builder import build_profile_battlefield_evidence
from configured_profile import ConfiguredProfile
from mechanical_magic_casting import MagicCastEvidence, enumerate_cast_allocations
from profiles import Profile


@dataclass(frozen=True)
class SpellCastingOptions:
    spell_id: str
    spell_name: str
    cast_value: int
    allocations: tuple[MagicCastEvidence, ...]
    conditional_rule_ids: tuple[str, ...]
    condition_verified: bool = False


@dataclass(frozen=True)
class ProfileMagicCastingEvidence:
    profile_id: str
    will_available: int
    spell_options: tuple[SpellCastingOptions, ...]
    excluded_spell_ids: tuple[str, ...]
    conditional_extra_casting_dice: int
    conditional_extra_casting_dice_sources: tuple[str, ...]
    conditional_extra_casts_per_opportunity: int
    conditional_extra_cast_sources: tuple[str, ...]
    evidence_status: str = "diagnostic_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def build_profile_magic_casting_evidence(
    profile: Profile | ConfiguredProfile,
    *,
    army=None,
    army_list=None,
    remaining_will: int | None = None,
) -> ProfileMagicCastingEvidence:
    """Enumerate legal known spells and explicit hypothetical Will allocations.

    The default Will comes from the profile's initial characteristic, not
    dynamically reconstructed battle state. Supplying remaining_will models
    an independently known resource state. Army rules are conditional: the
    caller must verify their operative requirements and spell eligibility.
    Only rules explicitly mapped in the existing analysis context are exposed.
    """
    if not isinstance(profile, (Profile, ConfiguredProfile)):
        raise TypeError("profile must be Profile or ConfiguredProfile")
    if (army is None) != (army_list is None):
        raise ValueError("army and army_list must be supplied together")
    base = profile.profile if isinstance(profile, ConfiguredProfile) else profile
    available_will = base.will if remaining_will is None else remaining_will
    if isinstance(available_will, bool) or not isinstance(available_will, int):
        raise TypeError("remaining_will must be an integer")
    if available_will < 0:
        raise ValueError("remaining_will cannot be negative")

    active_ids = ()
    extra_dice = 0
    extra_casts = 0
    dice_sources = ()
    cast_sources = ()
    if army_list is not None:
        context = build_army_analysis_context(army, army_list)
        active_ids = tuple(rule.id for rule in army_list.army_rules)
        extra_dice = context.extra_casting_dice_by_profile_id.get(base.id, 0)
        extra_casts = context.extra_spell_casts_by_profile_id.get(base.id, 0)
        dice_sources = tuple(rule_id for rule_id in ("DG_HIS_SPIRIT",)
                             if rule_id in active_ids and extra_dice)
        cast_sources = tuple(rule_id for rule_id in ("DG_POWER_OF_THE_NECROMANCER",)
                             if rule_id in active_ids and extra_casts)
        if extra_dice and not dice_sources:
            raise ValueError("additional casting dice lack mapped rule provenance")
        if extra_casts and not cast_sources:
            raise ValueError("extra casts lack mapped rule provenance")

    evidence = build_profile_battlefield_evidence(profile)
    available = tuple(evidence.available_spells)
    spell_options = []
    for assignment in available:
        allocations = enumerate_cast_allocations(
            cast_value=assignment.cast_value,
            will_available=available_will,
        )
        spell_options.append(SpellCastingOptions(
            spell_id=assignment.spell.id,
            spell_name=assignment.spell.name,
            cast_value=assignment.cast_value,
            allocations=allocations,
            conditional_rule_ids=(),
        ))
        if extra_dice:
            conditional = enumerate_cast_allocations(
                cast_value=assignment.cast_value,
                will_available=available_will,
                additional_dice=extra_dice,
                extra_dice_source="+".join(dice_sources),
            )
            spell_options.append(SpellCastingOptions(
                spell_id=assignment.spell.id,
                spell_name=assignment.spell.name,
                cast_value=assignment.cast_value,
                allocations=conditional,
                conditional_rule_ids=dice_sources,
            ))

    visible_ids = {id(item) for item in available}
    excluded = tuple(a.spell.id for a in base.spells if id(a) not in visible_ids)
    return ProfileMagicCastingEvidence(
        profile_id=base.id,
        will_available=available_will,
        spell_options=tuple(spell_options),
        excluded_spell_ids=excluded,
        conditional_extra_casting_dice=extra_dice,
        conditional_extra_casting_dice_sources=dice_sources,
        conditional_extra_casts_per_opportunity=extra_casts,
        conditional_extra_cast_sources=cast_sources,
    )

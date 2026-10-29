"""DEV-077-SMAUG-C4C/E — conditional Colossal Frame shooting context.

An explicit opt-in adapter for the existing structured shooting context. It
removes the *combat* In The Way roll only for an engaged, rule-bearing Smaug.
Terrain and qualifying model obstructions remain as supplied; Large Target
handling stays with the existing shooting engine. No scoring changes.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ColossalFrameContext:
    target_profile_id: str
    has_colossal_frame: bool
    target_engaged_in_combat: bool
    shooting_into_combat_required_roll: int | None = None
    terrain_required_rolls: tuple[int, ...] = ()
    model_obstructions: tuple = ()


@dataclass(frozen=True)
class ColossalFrameEvidence:
    can_target_while_engaged: bool
    shooting_into_combat_required_roll: int | None
    terrain_required_rolls: tuple[int, ...]
    model_obstructions: tuple
    exception_applied: bool
    evidence_status: str = 'conditional_shooting_context_only'
    dashboard_score: None = None
    scenario_score: None = None


def resolve_colossal_frame_context(context: ColossalFrameContext) -> ColossalFrameEvidence:
    """Produce inputs for ``get_shooting_wound_probability``.

    Caller must establish line of sight, actual engagement and geometry. The
    rule does not bypass terrain or unrelated model obstructions.
    """
    if not isinstance(context, ColossalFrameContext):
        raise TypeError('Expected ColossalFrameContext')
    if type(context.target_profile_id) is not str or not context.target_profile_id.strip():
        raise ValueError('Target profile identity required')
    if type(context.has_colossal_frame) is not bool or type(context.target_engaged_in_combat) is not bool:
        raise TypeError('Rule and engagement flags must be booleans')
    if context.shooting_into_combat_required_roll is not None and not (
        type(context.shooting_into_combat_required_roll) is int
        and 2 <= context.shooting_into_combat_required_roll <= 6
    ):
        raise ValueError('Combat In The Way roll must be 2–6 or None')
    if type(context.terrain_required_rolls) is not tuple or any(
        type(r) is not int or not 2 <= r <= 6 for r in context.terrain_required_rolls
    ):
        raise ValueError('Terrain In The Way rolls must be 2–6')
    if type(context.model_obstructions) is not tuple:
        raise TypeError('Model obstructions must be a tuple')
    rule_applies = (
        context.target_profile_id == 'SMAUG'
        and context.has_colossal_frame
        and context.target_engaged_in_combat
    )
    return ColossalFrameEvidence(
        can_target_while_engaged=rule_applies,
        shooting_into_combat_required_roll=(
            None if rule_applies else context.shooting_into_combat_required_roll
        ),
        terrain_required_rolls=context.terrain_required_rolls,
        model_obstructions=context.model_obstructions,
        exception_applied=rule_applies,
    )

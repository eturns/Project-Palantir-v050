"""DEV-077S-I2-H2-D: roster-backed Command diagnostic integration.

Uses the loaded Heroic Action relationships, never ability-tag weights.
All opportunities and coverage are declared evidence; no outcomes inferred.
"""
from dataclasses import dataclass

from army import Army
from command_action_declaration import (
    CommandActionDeclaration, CommandDecision, evaluate_command_declaration,
)
from command_coverage import (
    CommandCoverageObservation, CommandVerification, aggregate_command_coverage,
)
from hero_resource_state import HeroResourceState


@dataclass(frozen=True)
class FieldedCommandActor:
    model_id: str
    profile_id: str
    action_ids: tuple[str, ...]
    starting_might: int


@dataclass(frozen=True)
class CommandArmyEvidence:
    actors: tuple[FieldedCommandActor, ...]
    declarations: tuple
    remaining_resources: tuple[tuple[str, HeroResourceState], ...]
    coverage: object
    evidence_status: str = "roster_and_explicit_opportunities_only"
    dashboard_score: None = None
    scenario_score: None = None


def build_army_command_evidence(
    army: Army,
    declarations: tuple[CommandActionDeclaration, ...] = (),
    coverage: tuple[CommandCoverageObservation, ...] = (),
    other_might_spends: tuple[tuple[str, int], ...] = (),
) -> CommandArmyEvidence:
    """Account for declared Heroic Actions and other Might expenditures once.

    `other_might_spends` is an explicit cross-domain budget, e.g. Hero Hunting.
    It is not inferred from separate diagnostics. Coverage requires a permitted
    declaration with matching command ID and provider when command-linked.
    """
    if not isinstance(army, Army):
        raise TypeError("army must be Army")
    if not isinstance(declarations, tuple) or any(
        not isinstance(d, CommandActionDeclaration) for d in declarations
    ):
        raise TypeError("declarations must be CommandActionDeclaration tuple")
    if not isinstance(coverage, tuple) or any(
        not isinstance(c, CommandCoverageObservation) for c in coverage
    ):
        raise TypeError("coverage must be CommandCoverageObservation tuple")
    if not isinstance(other_might_spends, tuple):
        raise TypeError("other_might_spends must be tuple")
    actors, budgets, counts = [], {}, {}
    for entry in army.entries:
        if not entry.counts_as_model:
            continue
        profile = entry.configured_profile.profile
        for _ in range(entry.quantity):
            counts[profile.id] = counts.get(profile.id, 0) + 1
            model_id = f"{profile.id}#{counts[profile.id]}"
            ids = tuple(sorted({action.id for action in profile.heroic_actions}))
            actors.append(FieldedCommandActor(model_id, profile.id, ids, entry.get_attribute("might")))
            budgets[model_id] = HeroResourceState(
                remaining_might=entry.get_attribute("might"),
                remaining_will=entry.get_attribute("will"),
                remaining_fate=entry.get_attribute("fate"),
            )
    if len({d.event_id for d in declarations}) != len(declarations):
        raise ValueError("duplicate command event")
    for spend in other_might_spends:
        if (not isinstance(spend, tuple) or len(spend) != 2
                or not isinstance(spend[0], str)
                or isinstance(spend[1], bool) or not isinstance(spend[1], int)
                or spend[1] < 0):
            raise ValueError("invalid cross-domain Might spend")
        model_id, amount = spend
        if model_id not in budgets:
            raise ValueError("unknown cross-domain spender")
        state = budgets[model_id]
        if amount > state.remaining_might:
            raise ValueError("cross-domain Might budget exceeded")
        budgets[model_id] = HeroResourceState(
            state.remaining_might-amount, state.remaining_will, state.remaining_fate
        )
    by_id = {actor.model_id: actor for actor in actors}
    known_ids = tuple(sorted({
        action_id for actor in actors for action_id in actor.action_ids
    }))
    decisions = []
    for d in declarations:
        if d.actor_id not in by_id:
            raise ValueError("unknown Command actor")
        result = evaluate_command_declaration(
            d, known_action_ids=known_ids,
            available_action_ids=by_id[d.actor_id].action_ids,
            resources=budgets[d.actor_id],
        )
        decisions.append(result)
        budgets[d.actor_id] = result.remaining_resources
    permitted = {
        e.declaration.event_id: e.declaration.actor_id for e in decisions
        if e.decision is CommandDecision.PERMITTED
    }
    checked_coverage = []
    for observation in coverage:
        if observation.provider_id not in budgets or observation.recipient_id not in budgets:
            raise ValueError("coverage references non-fielded model")
        linked = (permitted.get(observation.command_id) == observation.provider_id)
        if not linked and observation.provider_permission is CommandVerification.VERIFIED_TRUE:
            raise ValueError("coverage claims permission without permitted command")
        checked_coverage.append(observation)
    return CommandArmyEvidence(
        actors=tuple(actors), declarations=tuple(decisions),
        remaining_resources=tuple(sorted(budgets.items())),
        coverage=aggregate_command_coverage(tuple(checked_coverage)),
    )

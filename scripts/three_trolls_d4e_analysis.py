"""DEV-077-TT-D4E: validated imported-purchase diagnostic integration.

Use at the MESBG List Builder orchestration boundary where ArmyDefinition exists.
The 12 paid effects are available through existing pure resolvers, but no
battlefield contexts or calibrated scoring changes are inferred.
"""
from __future__ import annotations
from dataclasses import dataclass
from three_trolls_hoard import build_hoard_evidence, HoardEvidence
from three_trolls_upgrades import THREE_TROLLS_ARMY_LIST_ID
from three_trolls_d4a_effects import full_bellies_starting_resources
from three_trolls_d4d_effects import cover_of_darkness


@dataclass(frozen=True)
class ThreeTrollsUpgradeAnalysis:
    hoard: HoardEvidence
    available_effect_keys: tuple[str, ...]
    inactive_effect_keys: tuple[str, ...]
    starting_resources_by_profile_id: dict
    cave_dweller_by_profile_id: dict
    battlefield_status: str


def _starting_resource(configured_profile, resource: str) -> int:
    """Read resources from real ConfiguredProfile or the existing test adapter.

    Real ConfiguredProfile holds canonical base values in ``profile`` and does
    not expose ``get_attribute``. The adapter used by earlier E1/D4E tests
    does expose that method, so retain compatibility without monkey-patching.
    """
    profile = getattr(configured_profile, "profile", None)
    if profile is not None:
        value = getattr(profile, resource)
    else:
        getter = getattr(configured_profile, "get_attribute", None)
        if not callable(getter):
            raise TypeError("Configured model has no starting resource interface")
        value = getter(resource)
    if type(value) is not int or value < 0:
        raise ValueError(f"Invalid starting {resource} resource")
    return value


def build_three_trolls_upgrade_analysis(definition, army) -> ThreeTrollsUpgradeAnalysis | None:
    """Use the imported selection and *actual* purchase ledger as authority.

    Results are intentionally uncalibrated diagnostic evidence. Starting
    resources are explicit predictions, not mutations of Army profiles.
    """
    # Legacy service tests use lightweight definition stubs without an army
    # list identifier. Such objects are not Three Trolls imports. Keep the
    # strict purchase-ledger validation for explicitly tagged Three Trolls.
    if getattr(definition, "army_list_id", None) != THREE_TROLLS_ARMY_LIST_ID:
        return None
    hoard = build_hoard_evidence(definition)
    if hoard is None:
        return None
    models = tuple(army.fielded_models())
    profiles = {}
    for model in models:
        if model.profile_id not in ('TT_BILL', 'TT_BERT', 'TT_TOM'):
            continue
        cfg = model.configured_profile
        if cfg is None:
            raise ValueError('Three Trolls require configured profiles')
        if model.profile_id in profiles:
            raise ValueError('Duplicate named Troll model')
        profiles[model.profile_id] = cfg
    expected = {'TT_BILL', 'TT_BERT', 'TT_TOM'}
    if set(profiles) != expected:
        raise ValueError('Three Trolls army must field Bill, Bert and Tom exactly once')
    resources = {}
    cave_dweller = {}
    for pid, cfg in profiles.items():
        resources[pid] = full_bellies_starting_resources(
            hoard, pid,
            base_might=_starting_resource(cfg, 'might'),
            base_will=_starting_resource(cfg, 'will'),
            base_fate=_starting_resource(cfg, 'fate'),
        )
        cave_dweller[pid] = cover_of_darkness(hoard, pid).grants_cave_dweller
    return ThreeTrollsUpgradeAnalysis(
        hoard=hoard,
        available_effect_keys=tuple(u.effect_key for u in hoard.upgrades if u.activated),
        inactive_effect_keys=tuple(u.effect_key for u in hoard.upgrades if not u.activated),
        starting_resources_by_profile_id=resources,
        cave_dweller_by_profile_id=cave_dweller,
        battlefield_status='conditional_not_evaluated',
    )

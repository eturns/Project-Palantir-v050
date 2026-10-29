"""DEV-077-SMAUG-C5D/E contract tests (isolated + service source contract)."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from smaug_magic_analysis import build_smaug_magic_analysis


class DummyArmy:
    def __init__(self, profile, *, model_count=1):
        self._profile = profile
        self._count = model_count

    def fielded_models(self):
        return (SimpleNamespace(counts_as_model=True, configured_profile=self._profile),)

    def model_count(self):
        return self._count


def test_non_army_rejected():
    with pytest.raises(TypeError, match="real Army"):
        build_smaug_magic_analysis(object())


def test_service_exposes_opt_in_separate_key_without_touching_scores():
    import inspect
    from services.army_analysis_service import analyse_imported_army
    src = inspect.getsource(analyse_imported_army)
    assert "mechanical_smaug_magic" in src
    assert "build_smaug_magic_analysis(army)" in src
    assert "offence_score = calculate_army_offensive_output_density(army)" in src


def test_no_changes_to_permanent_resource_totals():
    from army_resource_totals import calculate_army_resource_totals
    import inspect
    assert "temporary_resource" not in inspect.getsource(calculate_army_resource_totals)


def test_rule_eligible_grant_matches_c5c_contract():
    from resource_owner import ResourceOwner
    from resource_use_permission import ResourceType
    from special_rule_temporary_resource_grants import get_special_rule_temporary_resource_grants
    owner = ResourceOwner("SMAUG:1:1")
    grants = get_special_rule_temporary_resource_grants(
        owner, frozenset({"DESOLATOR_OF_THE_NORTH"}))
    assert sum(g.amount for g in grants if g.resource_type == ResourceType.WILL) == 1


def test_rule_absent_never_grants_will():
    from resource_owner import ResourceOwner
    from resource_use_permission import ResourceType
    from special_rule_temporary_resource_grants import get_special_rule_temporary_resource_grants
    owner = ResourceOwner("OTHER:1:1")
    assert not any(g.resource_type == ResourceType.WILL for g in
                   get_special_rule_temporary_resource_grants(owner, frozenset()))


def test_c5d_results_do_not_feed_rating_pipeline():
    import inspect
    from services.army_analysis_service import analyse_imported_army
    source = inspect.getsource(analyse_imported_army)
    result_line = "result['mechanical_smaug_magic'] = mechanical_smaug_magic"
    assert result_line in source
    assert source.index(result_line) > source.index("battlefield_assessments = assess_battlefield")


def make_army(rule_present=True, profile_id='SMAUG'):
    from army import Army
    from profiles import Profile
    from profile_special_rule_assignment import ProfileSpecialRuleAssignment
    from special_rule import SpecialRule
    from database.rule_category import RuleCategory
    profile = Profile(
        id=profile_id, name='Test', points=700, movement=12, fight=9,
        shooting='2+', strength=9, defence=9, attacks=4, wounds=20,
        courage='4+', intelligence='4+', might=3, will=6, fate=0,
        max_in_army=1)
    if rule_present:
        profile.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule('DESOLATOR_OF_THE_NORTH', 'Desolator of the North', RuleCategory.MAGIC)))
    army = Army()
    army.add_profile(profile)
    return army


def test_real_army_reports_permanent_and_conditional_will_separately():
    result = build_smaug_magic_analysis(make_army())
    assert result.permanent_will == 6
    assert result.temporary_will_this_turn == 1
    assert result.hypothetical_available_will == 7
    assert result.permanent_casting.will_available == 6
    assert result.conditional_casting.will_available == 7
    assert result.dashboard_score is None and result.scenario_score is None


def test_rule_absent_must_not_claim_grant():
    result = build_smaug_magic_analysis(make_army(rule_present=False))
    assert result.temporary_will_this_turn == 0
    assert result.conditional_casting is None
    assert result.permanent_will == 6


def test_other_army_not_assigned_smaug_evidence():
    assert build_smaug_magic_analysis(make_army(profile_id='OTHER')) is None

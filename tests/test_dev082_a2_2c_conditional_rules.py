"""DEV-082-A2-2C — conditional target-keyword evidence.
Author: Edward Turns (Project Lead)
"""
import pytest
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule
from offence_charge_state_evidence import calculate_charge_state_offence_evidence as score


def fighter(*rules):
    p = Profile(id='DEV082_CONDITIONAL', name='Test', points=20, movement=6,
                fight=4, shooting='4+', strength=4, defence=5, attacks=1,
                wounds=1, courage='4+', intelligence='4+', might=0, will=0,
                fate=0, max_in_army=1)
    for name, parameter in rules:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id=name, name=name, category=RuleCategory.SPECIAL),
            parameter=parameter))
    return ConfiguredProfile(profile=p)


def test_hatred_needs_matching_target_keyword():
    a = fighter(('HATRED', 'ORC'))
    baseline = score(a)
    mismatch = score(a, target_keywords=('ELF',))
    match = score(a, target_keywords=('ORC',))
    assert baseline.uncharged == pytest.approx(mismatch.uncharged)
    assert match.uncharged > baseline.uncharged
    assert baseline.target_keyword_status == 'unqualified_benchmark_keywords'
    assert match.target_keyword_status == 'explicit_target_keywords'


def test_ancient_enemies_needs_matching_target_keyword():
    a = fighter(('ANCIENT_ENEMIES', 'ELF'))
    assert score(a, target_keywords=('elf',)).uncharged > score(a, target_keywords=('ORC',)).uncharged


def test_venom_remains_target_independent():
    a = fighter(('VENOM', None))
    assert score(a).uncharged == pytest.approx(score(a, target_keywords=('ORC',)).uncharged)
    assert score(a).uncharged > score(fighter()).uncharged


def test_plain_profile_does_not_gain_bonus_from_target_identity():
    assert score(fighter()).uncharged == pytest.approx(score(fighter(), target_keywords=('ORC',)).uncharged)


def test_keywords_normalised_and_deduplicated():
    e = score(fighter(), target_keywords=(' orc ', 'ORC', 'Elf'))
    assert e.target_keywords == ('ELF', 'ORC')
    assert e.target_keyword_status == 'explicit_target_keywords'


def test_empty_explicit_context_distinguished_from_unknown():
    assert score(fighter(), target_keywords=()).target_keyword_status == 'explicit_target_keywords'
    assert score(fighter()).target_keyword_status == 'unqualified_benchmark_keywords'


@pytest.mark.parametrize('bad', [[], 'ORC', ('',), (' ',), (1,), ('ORC', None)])
def test_invalid_keyword_input_rejected(bad):
    with pytest.raises(TypeError, match='target_keywords'):
        score(fighter(), target_keywords=bad)


def test_output_remains_unrated_and_not_weighted():
    e = score(fighter(('HATRED', 'ORC')), target_keywords=('ORC',))
    assert e.weighted is None
    assert e.status == 'conditional_display_only_not_calibrated'


def test_trap_remains_independent_of_target_keyword_context():
    a = fighter(('HATRED', 'ORC'))
    plain = score(a, target_keywords=('ORC',), defender_trapped=False)
    trapped = score(a, target_keywords=('ORC',), defender_trapped=True)
    assert trapped.uncharged > plain.uncharged
    assert trapped.trap_context_status == 'explicit_trapped'

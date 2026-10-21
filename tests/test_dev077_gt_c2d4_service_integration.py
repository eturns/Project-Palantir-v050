"""DEV-077-GT-C2D4 integration acceptance: rule evidence + score invariance."""
from fractions import Fraction
import pytest

from army import Army
from loader import load_all_profiles
from rule_loader import load_special_rules
from relationship_loader import load_profile_special_rules
from configured_profile import ConfiguredProfile
from goblin_king_defence_integration import BlubberyAttackContext
from goblin_king_projectile import ProjectileContext
from goblin_king_relentless_advance_army_evidence import ChargePathContext
from gundabad_relentless_advance import FriendlyContact
from goblin_king_mechanical_evidence import build_goblin_king_mechanical_evidence
from services import army_analysis_service as service


@pytest.fixture(scope='module')
def profiles():
    data = {p.id: p for p in load_all_profiles()}
    load_profile_special_rules(data, load_special_rules())
    return {k: ConfiguredProfile(data[k]) for k in ('GT_KING', 'GT_WARRIOR', 'GUNDABAD_OGRE')}


def army(*models):
    a = Army()
    for cfg in models:
        a.add_configured_profile(cfg)
    return a


def test_unknown_contexts_are_not_zero(profiles):
    e = build_goblin_king_mechanical_evidence(army(profiles['GT_KING'], profiles['GT_WARRIOR']))
    assert e.defence_context_supplied is False
    assert e.defence.contexts_supplied == 0
    assert e.shooting[0].expected_target_wounds is None
    assert e.movement_offence[0].expected_friendly_hit_wounds is None
    assert e.movement_offence[0].expected_enemy_wounds is None


def test_non_goblin_army_gets_no_evidence(profiles):
    assert build_goblin_king_mechanical_evidence(army(profiles['GUNDABAD_OGRE'])) is None


def test_defence_provenance_is_passed(profiles):
    a=army(profiles['GT_KING'])
    e=build_goblin_king_mechanical_evidence(
        a,defence_attack_contexts=(BlubberyAttackContext(False,False,False),))
    assert e.defence_context_supplied
    assert e.defence.expected_wounds_remaining==Fraction(1,3)


def test_service_preserves_scores(monkeypatch, profiles):
    a=army(profiles['GT_KING'],profiles['GT_WARRIOR'])
    # Stub unrelated expensive scoring and data structures identically between runs.
    monkeypatch.setattr(service,'calculate_army_metric_densities',lambda *_:'densities')
    monkeypatch.setattr(service,'calculate_army_offensive_output_density',lambda *_:3)
    monkeypatch.setattr(service,'calculate_army_shooting_output_density',lambda **_:Fraction(1,2))
    monkeypatch.setattr(service,'normalise_shooting_output_density',lambda *_:4)
    monkeypatch.setattr(service,'build_shooting_benchmark_defender',lambda:None)
    monkeypatch.setattr(service,'calculate_mechanical_defence_diagnostics',lambda *_:{})
    monkeypatch.setattr(service,'build_mobility_integration_contract',lambda *_:{})
    monkeypatch.setattr(service,'audit_army_magic_completeness',lambda *_:type('Audit',(),{'is_complete':False})())
    monkeypatch.setattr(service,'assess_army_metrics',lambda *a,**kw:kw)
    monkeypatch.setattr(service,'assess_battlefield',lambda a:a)
    base=service.analyse_imported_army(a,None,500,None)
    firing=service.analyse_imported_army(
        a,None,500,None,
        goblin_king_defence_attack_contexts=(BlubberyAttackContext(False,False,True),),
    )
    for key in ('metric_assessments','battlefield_assessments','metric_densities','metrics'):
        assert firing[key]==base[key]
    assert firing['mechanical_goblin_king'].defence.expected_wounds_remaining==Fraction(1,2)


def test_missing_king_rejects_supplied_context(profiles):
    with pytest.raises(ValueError,match='without a Goblin King'):
        build_goblin_king_mechanical_evidence(army(profiles['GUNDABAD_OGRE']),
            defence_attack_contexts=())

"""DEV-078-AoG-E2 banner effects acceptance.

Author: Edward Turns (Project Lead).
"""
from fractions import Fraction
from types import SimpleNamespace
import pytest
from gundabad_raise_the_banners import Banner, BannerState
from gundabad_banner_effects import (
    banner_reroll_eligible, free_heroic_march_eligible,
    heroic_march_cost, angmar_prevention_probability,
    resolve_angmar_prevention, with_dol_guldur_banner_support,
)
from loader import load_all_profiles
from configured_profile import ConfiguredProfile
from profile_classification import HeroicStatus


@pytest.fixture(scope="module")
def profiles():
    from relationship_loader import load_profile_special_rules
    from rule_loader import load_special_rules
    profiles = {p.id: p for p in load_all_profiles()}
    load_profile_special_rules(profiles=profiles, special_rules=load_special_rules())
    return profiles


def state(banner):
    return BannerState(turn=1,active_banner=banner,last_raised_banner=banner,last_raised_turn=1)


def test_gundabad_warrior_gets_dol_guldur_banner(profiles):
    assert banner_reroll_eligible(state(Banner.DOL_GULDUR),profiles["GUNDABAD_ORC_WARRIOR"])


def test_gundabad_hero_gets_dol_guldur_banner(profiles):
    assert banner_reroll_eligible(state(Banner.DOL_GULDUR),profiles["AZOG_THE_DEFILER"])


@pytest.mark.parametrize("id",["IH_WR","BOFUR_CHAMPION_OF_EREBOR","GT_WARRIOR"])
def test_other_factions_no_dol_guldur_banner(profiles,id):
    assert not banner_reroll_eligible(state(Banner.DOL_GULDUR),profiles[id])


def test_other_banner_does_not_enable_reroll(profiles):
    assert not banner_reroll_eligible(state(Banner.ANGMAR), profiles["AZOG_THE_DEFILER"])


def test_gundabad_hero_free_march(profiles):
    assert free_heroic_march_eligible(state(Banner.GUNDABAD),profiles["AZOG_THE_DEFILER"])


def test_gundabad_warrior_no_free_march(profiles):
    assert not free_heroic_march_eligible(state(Banner.GUNDABAD),profiles["GUNDABAD_ORC_WARRIOR"])


def test_enemy_hero_no_free_march(profiles):
    assert not free_heroic_march_eligible(state(Banner.GUNDABAD),profiles["IH_DAIN"])


def test_other_banner_no_free_march(profiles):
    assert not free_heroic_march_eligible(state(Banner.ANGMAR),profiles["AZOG_THE_DEFILER"])


def test_free_march_zero_might(profiles):
    outcome=heroic_march_cost(state(Banner.GUNDABAD),profiles["AZOG_THE_DEFILER"],can_declare_heroic_march=True)
    assert outcome.eligible_for_free_march and outcome.might_cost==0


def test_no_action_not_granted(profiles):
    outcome=heroic_march_cost(state(Banner.GUNDABAD),profiles["AZOG_THE_DEFILER"],can_declare_heroic_march=False)
    assert not outcome.eligible_for_free_march and outcome.might_cost==1


def test_inactive_banner_normal_march_cost(profiles):
    outcome=heroic_march_cost(BannerState(),profiles["AZOG_THE_DEFILER"],can_declare_heroic_march=True)
    assert outcome.might_cost==1


def test_natural_six_angmar_prevention_for_regular_gundabad(profiles):
    p=profiles["GUNDABAD_ORC_WARRIOR"]
    assert angmar_prevention_probability(state(Banner.ANGMAR),p)==Fraction(1,6)
    assert not resolve_angmar_prevention(state(Banner.ANGMAR),p,5)
    assert resolve_angmar_prevention(state(Banner.ANGMAR),p,6)


def test_enemy_no_angmar_prevention(profiles):
    assert angmar_prevention_probability(state(Banner.ANGMAR),profiles["IH_WR"])==0


def test_angmar_expired_does_not_grant_prevention(profiles):
    assert angmar_prevention_probability(BannerState(),profiles["GUNDABAD_ORC_WARRIOR"])==0


def test_berserker_oblivious_to_pain_5_plus(profiles):
    p=profiles["GUNDABAD_BERSERKER"]
    assert angmar_prevention_probability(state(Banner.ANGMAR),p)==Fraction(1,3)
    assert resolve_angmar_prevention(state(Banner.ANGMAR),p,5)
    assert not resolve_angmar_prevention(state(Banner.ANGMAR),p,4)


def test_berserker_normal_oblivious_six_plus(profiles):
    p=profiles["GUNDABAD_BERSERKER"]
    assert angmar_prevention_probability(BannerState(),p)==Fraction(1,6)
    assert resolve_angmar_prevention(BannerState(),p,6)
    assert not resolve_angmar_prevention(BannerState(),p,5)


def test_configured_profile_supported(profiles):
    p=ConfiguredProfile(profiles["AZOG_THE_DEFILER"])
    assert free_heroic_march_eligible(state(Banner.GUNDABAD),p)


@pytest.mark.parametrize("bad",[0,7,True,3.4])
def test_invalid_die_rejected(profiles,bad):
    with pytest.raises(ValueError):
        resolve_angmar_prevention(state(Banner.ANGMAR),profiles["GUNDABAD_ORC_WARRIOR"],bad)


@pytest.mark.parametrize("bad",[-1,True,1.5])
def test_bad_might_cost_rejected(profiles,bad):
    with pytest.raises(ValueError):
        heroic_march_cost(state(Banner.GUNDABAD),profiles["AZOG_THE_DEFILER"],can_declare_heroic_march=True,base_might_cost=bad)


def test_invalid_profile_rejected():
    with pytest.raises(TypeError):
        banner_reroll_eligible(state(Banner.DOL_GULDUR),object())

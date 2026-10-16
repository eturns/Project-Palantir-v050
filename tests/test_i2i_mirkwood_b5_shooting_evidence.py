"""B5 real runtime and shooting resolver integration checks."""
import pytest
from i2i_mirkwood_b5_shooting_evidence import measure, load_reference_army, EXPECTED
from shooting_attack_count import ShootingMode, get_effective_shooting_attack_count
from army_shooting_capability import resolve_army_ranged_shooters

@pytest.fixture(scope="module")
def evidence():
    return measure()

def test_real_roster_composition(evidence):
    assert evidence["composition"]==EXPECTED

def test_army_points(evidence):
    assert evidence["points"]==700

def test_model_count(evidence):
    assert evidence["models"]==33

def test_all_models_equipped_with_recognised_bows(evidence):
    assert evidence["recognised_bows"]==33
    assert evidence["bow_model_counts"]==EXPECTED
    assert not evidence["unexpected_weapon_records"]

def test_legolas_three_normal_attacks(evidence):
    assert evidence["attacks_by_profile"]["MW_LEGOLAS"]==3

def test_tauriel_two_normal_attacks(evidence):
    assert evidence["attacks_by_profile"]["MW_TAURIEL"]==2

def test_ranger_captain_one_attack(evidence):
    assert evidence["attacks_by_profile"]["MW_RANGER_CAPTAIN"]==1

def test_thirty_rangers_one_each(evidence):
    assert evidence["attacks_by_profile"]["MW_RANGER"]==30

def test_total_normal_shots(evidence):
    assert evidence["normal_shooting_attacks"]==36

def test_pinpoint_not_double_counted():
    army=load_reference_army()
    legolas=next(c for c,w in resolve_army_ranged_shooters(army) if c.profile.id=="MW_LEGOLAS")
    assert get_effective_shooting_attack_count(legolas)==3
    assert get_effective_shooting_attack_count(legolas,mode=ShootingMode.PINPOINT)==1

def test_no_unapproved_scoring(evidence):
    assert not evidence["calibration_anchors_approved"]
    assert not evidence["production_scoring_modified"]

def test_all_evidence_gates(evidence):
    assert evidence["measurement_qualified"], evidence["blockers"]

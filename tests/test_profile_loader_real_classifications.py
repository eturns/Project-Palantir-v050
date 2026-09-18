from loader import load_profile
from profile_classification import (
    HeroicStatus,
    ModelType,
)

def test_real_dol_guldur_profiles_load_classifications():
    witch_king = load_profile("DG_WK")
    giant_spider = load_profile("DG_MGS")

    assert witch_king.heroic_status is HeroicStatus.HERO

    assert witch_king.model_types == {
        ModelType.INFANTRY,
    }

    assert witch_king.races == {
        "SPIRIT",
        "RINGWRAITH",
    }

    assert giant_spider.heroic_status is HeroicStatus.WARRIOR

    assert giant_spider.model_types == {
        ModelType.BEAST,
        ModelType.INFANTRY,
    }

    assert giant_spider.races == {
        "SPIDER",
    }

def test_gundabad_catapult_troll_has_combined_model_types():
    profile = load_profile("GUNDABAD_CATAPULT_TROLL")

    assert profile.points == 180
    assert profile.wounds == 5
    assert profile.heroic_status is HeroicStatus.HERO

    assert profile.model_types == {
        ModelType.INFANTRY,
        ModelType.MONSTER,
        ModelType.SIEGE_ENGINE,
    }

    assert profile.races == {"TROLL"}

def test_troll_brute_profiles_load_expected_classifications():
    troll_brute = load_profile("TROLL_BRUTE")
    orc_commander = load_profile("ORC_COMMANDER")

    assert troll_brute.points == 0
    assert troll_brute.max_in_army == 0
    assert troll_brute.heroic_status is None
    assert troll_brute.model_types == {
        ModelType.WAR_BEAST,
    }
    assert troll_brute.races == {"TROLL"}

    assert orc_commander.points == 0
    assert orc_commander.max_in_army == 0
    assert orc_commander.heroic_status is HeroicStatus.HERO
    assert orc_commander.model_types == {
        ModelType.INFANTRY,
    }
    assert orc_commander.races == {"ORC"}

def test_bofur_champion_of_erebor_loads_from_production_data():
    bofur = load_profile("BOFUR_CHAMPION_OF_EREBOR")

    assert bofur.name == (
        "Bofur the Dwarf, Champion of Erebor"
    )
    assert bofur.points == 65
    assert bofur.max_in_army == 1
    assert bofur.heroic_status is HeroicStatus.HERO
    assert bofur.model_types == {
        ModelType.INFANTRY,
    }
    assert bofur.races == {
        "DWARF",
    }
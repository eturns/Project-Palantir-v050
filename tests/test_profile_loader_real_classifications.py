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

def test_rise_of_the_necromancer_missing_profiles_load():
    keeper = load_profile("DG_KEEPER")
    captain = load_profile("DG_HOC")
    warrior = load_profile("DG_HOW")
    warg_rider = load_profile("DG_HOWR")
    fell_warg = load_profile("DG_FW")
    castellan = load_profile("DG_CASTELLAN")

    assert keeper.points == 80
    assert keeper.fight == 5
    assert keeper.strength == 5
    assert keeper.defence == 6
    assert keeper.attacks == 3
    assert keeper.wounds == 2
    assert keeper.might == 3
    assert keeper.will == 3
    assert keeper.fate == 0
    assert keeper.max_in_army == 1
    assert keeper.heroic_status is HeroicStatus.HERO
    assert keeper.model_types == {
        ModelType.INFANTRY,
    }
    assert keeper.races == {"ORC"}

    assert captain.points == 45
    assert captain.heroic_status is HeroicStatus.HERO
    assert captain.model_types == {
        ModelType.INFANTRY,
    }
    assert captain.races == {"ORC"}

    assert warrior.points == 8
    assert warrior.heroic_status is HeroicStatus.WARRIOR
    assert warrior.model_types == {
        ModelType.INFANTRY,
    }

    assert warg_rider.points == 15
    assert warg_rider.movement == 6
    assert warg_rider.model_types == {
        ModelType.CAVALRY,
    }
    assert warg_rider.races == {"ORC"}

    assert fell_warg.points == 8
    assert fell_warg.movement == 10
    assert fell_warg.model_types == {
        ModelType.BEAST,
        ModelType.INFANTRY,
    }
    assert fell_warg.races == {"WARG"}

    assert castellan.points == 50
    assert castellan.might == 0
    assert castellan.will == 10
    assert castellan.fate == 0
    assert castellan.heroic_status is HeroicStatus.HERO
    assert castellan.model_types == {
        ModelType.INFANTRY,
    }
    assert castellan.races == {"SPIRIT"}
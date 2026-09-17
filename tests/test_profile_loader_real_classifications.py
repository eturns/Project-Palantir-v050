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
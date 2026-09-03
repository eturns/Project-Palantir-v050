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
from pathlib import Path

from loader import _load_profiles_from_file
from profile_classification import (
    HeroicStatus,
    ModelType,
)


def test_profile_loader_reads_profile_classifications(
    tmp_path: Path,
):
    csv_path = tmp_path / "profiles.csv"

    csv_path.write_text(
        (
            "id,name,points,movement,base_size_mm,"
            "fight,shooting,strength,defence,"
            "attacks,wounds,courage,intelligence,"
            "might,will,fate,max_in_army,"
            "heroic_status,model_types,races\n"
            "TEST_HERO,Test Hero,100,6\",25,"
            "5,4+,4,6,2,2,4+,4+,"
            "2,2,2,1,"
            "HERO,BEAST|INFANTRY,SPIRIT|RINGWRAITH\n"
        ),
        encoding="utf-8",
    )

    profiles = _load_profiles_from_file(
        str(csv_path),
    )

    assert len(profiles) == 1

    profile = profiles[0]

    assert profile.heroic_status is HeroicStatus.HERO

    assert profile.model_types == {
        ModelType.BEAST,
        ModelType.INFANTRY,
    }

    assert profile.races == {
        "SPIRIT",
        "RINGWRAITH",
    }
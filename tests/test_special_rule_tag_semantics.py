import csv
from pathlib import Path


SPECIAL_RULE_TAGS_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "rules"
    / "special_rule_tags.csv"
)


def load_rule_tags(rule_id: str) -> dict[str, float]:
    with SPECIAL_RULE_TAGS_PATH.open(
        newline="",
        encoding="utf-8",
    ) as file:
        rows = csv.DictReader(file)

        return {
            row["ability_tag_id"]: float(row["weight"])
            for row in rows
            if row["special_rule_id"] == rule_id
        }


def test_bane_of_kings_is_generic_offence_and_shooting_not_hero_hunting():
    tags = load_rule_tags("BANE_OF_KINGS")

    assert "OFFENCE" in tags
    assert "SHOOTING" in tags
    assert "HERO_HUNTING" not in tags


def test_executioner_is_offence_not_hero_hunting():
    tags = load_rule_tags("EXECUTIONER")

    assert "OFFENCE" in tags
    assert "HERO_HUNTING" not in tags


def test_drain_soul_is_offence_not_hero_hunting():
    tags = load_rule_tags("DRAIN_SOUL")

    assert "OFFENCE" in tags
    assert "HERO_HUNTING" not in tags


def test_master_of_the_nazgul_is_defence_not_command():
    tags = load_rule_tags("MASTER_OF_THE_NAZGUL")

    assert "DEFENCE" in tags
    assert "COMMAND" not in tags


def test_unholy_resurrection_is_defence_not_objective():
    tags = load_rule_tags("UNHOLY_RESURRECTION")

    assert "DEFENCE" in tags
    assert "OBJECTIVE" not in tags
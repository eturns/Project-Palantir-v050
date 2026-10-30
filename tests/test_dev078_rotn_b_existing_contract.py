"""DEV-078-ROTN-B: read-only baseline contract at Smaug closure c9db857.

Place in tests/. Run: py -3.14 -m pytest -q tests/test_dev078_rotn_b_existing_contract.py
These tests establish EXISTING behaviour; they do not claim complete army-rule support.
"""
import csv
from pathlib import Path
from types import SimpleNamespace

from army_analysis_context_builder import build_army_analysis_context
from mechanical_magic_casting import calculate_cast_evidence

ROOT = Path(__file__).resolve().parents[1]
ARMY_ID = "DG_ROTN"
NECROMANCER_ID = "DG_NEC"
POWER = "DG_POWER_OF_THE_NECROMANCER"
SPIRIT = "DG_HIS_SPIRIT"


def _rows(relative):
    with (ROOT / relative).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _context(*ids):
    army_list = SimpleNamespace(army_rules=[SimpleNamespace(id=rule_id) for rule_id in ids])
    return build_army_analysis_context(object(), army_list)


def test_necromancer_army_registered_once():
    rows = [row for row in _rows("data/factions/army_lists.csv") if row["id"] == ARMY_ID]
    assert len(rows) == 1


def test_existing_army_rule_ids_match_canonical_two():
    rows = [row for row in _rows("data/factions/army_rules.csv") if row["army_list_id"] == ARMY_ID]
    assert {row["id"] for row in rows} == {POWER, SPIRIT}
    assert len(rows) == 2


def test_existing_rule_context_provides_necromancer_modifiers_only():
    ctx = _context(POWER, SPIRIT)
    assert ctx.extra_spell_casts_by_profile_id == {NECROMANCER_ID: 1}
    assert ctx.extra_casting_dice_by_profile_id == {NECROMANCER_ID: 1}


def test_empty_army_rules_have_no_necromancer_modifiers():
    ctx = _context()
    assert ctx.extra_spell_casts_by_profile_id == {}
    assert ctx.extra_casting_dice_by_profile_id == {}


def test_free_casting_die_is_not_a_free_will_refund():
    evidence = calculate_cast_evidence(
        cast_value=4, will_available=3, will_spent=1,
        additional_dice=1, extra_dice_source=SPIRIT,
    )
    assert evidence.dice_total == 2
    assert evidence.will_remaining_after_attempt == 2
    assert evidence.extra_dice_source == SPIRIT
    assert evidence.dashboard_score is None
    assert evidence.scenario_score is None

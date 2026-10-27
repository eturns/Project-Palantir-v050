"""Regression guards for non-Troll imports using partial definition doubles."""
from types import SimpleNamespace
import pytest
from three_trolls_d4e_analysis import build_three_trolls_upgrade_analysis


class PoisonArmy:
    def fielded_models(self):
        raise AssertionError("Non-Troll analysis must not inspect Troll models")


def test_legacy_lightweight_definition_is_skipped():
    assert build_three_trolls_upgrade_analysis(SimpleNamespace(), PoisonArmy()) is None


def test_non_troll_definition_skips_missing_hoard_fields():
    assert build_three_trolls_upgrade_analysis(
        SimpleNamespace(army_list_id="MORDOR"), PoisonArmy()
    ) is None


def test_null_army_list_id_skipped():
    assert build_three_trolls_upgrade_analysis(
        SimpleNamespace(army_list_id=None), PoisonArmy()
    ) is None


def test_explicit_three_trolls_still_requires_upgrade_ledger():
    with pytest.raises(AttributeError):
        build_three_trolls_upgrade_analysis(
            SimpleNamespace(army_list_id="THREE_TROLLS"), PoisonArmy()
        )

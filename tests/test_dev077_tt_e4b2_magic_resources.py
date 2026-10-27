"""DEV-077-TT-E4B2: army Magic inventory/contract use purchased starting Will."""
from types import SimpleNamespace
import pytest
from test_dev077_tt_e2_real_builder_service import real_army

@pytest.mark.parametrize('upgrades,expected_will', [
    ((), 1),
    (("Full Bellies",), 3),
])
def test_inventory_receives_effective_will_for_each_troll(monkeypatch, upgrades, expected_will):
    import mechanical_magic_army_evidence as module
    _, army, _ = real_army(upgrades)
    seen = []
    def fake_profile_evidence(profile, *, remaining_will=None, **kwargs):
        seen.append((profile.profile.id, remaining_will))
        return SimpleNamespace(spell_options=())
    monkeypatch.setattr(module, 'build_profile_magic_casting_evidence', fake_profile_evidence)
    module.build_army_magic_evidence(army)
    assert len(seen) == 3
    assert {profile_id for profile_id, _ in seen} == {'TT_BILL', 'TT_BERT', 'TT_TOM'}
    assert {will for _, will in seen} == {expected_will}

@pytest.mark.parametrize('upgrades,expected_will', [
    ((), 1),
    (("Full Bellies",), 3),
])
def test_magic_contract_receives_effective_will_for_each_troll(monkeypatch, upgrades, expected_will):
    import mechanical_magic_army_contract as module
    _, army, _ = real_army(upgrades)
    seen = []
    def fake_profile_evidence(profile, *, remaining_will=None, **kwargs):
        seen.append((profile.profile.id, remaining_will))
        return SimpleNamespace(spell_options=())
    monkeypatch.setattr(module, 'build_profile_magic_casting_evidence', fake_profile_evidence)
    # Real inventory sees no caster for these synthetic troll fixtures.
    contract = module.build_army_magic_contract(army)
    assert contract.caster_count == 0
    assert len(seen) == 3
    assert {profile_id for profile_id, _ in seen} == {'TT_BILL', 'TT_BERT', 'TT_TOM'}
    assert {will for _, will in seen} == {expected_will}


def test_full_bellies_still_does_not_mutate_profile_base_will():
    _, army, _ = real_army(("Full Bellies",))
    assert all(entry.profile.will == 1 for entry in army.entries)
    assert all(entry.get_attribute('will') == 3 for entry in army.entries)

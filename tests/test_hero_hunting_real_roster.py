"""Production-fidelity tests: no synthetic profile attributes or scoring."""
import pytest
from army import Army
from hero_hunting_real_roster import collect_real_army_roster

from tests.test_dev077s_i2f_f4_a2_real_army_magic import real_armies as fixture_armies


@pytest.fixture(scope="module")
def real_armies(fixture_armies):
    return fixture_armies


def test_necromancer_roster_has_nine_real_spells(real_armies):
    (rise,_),_=real_armies
    roster=collect_real_army_roster("rise",rise)
    assert any(len(m.spell_cast_values)==9 and
               ("CHILL_SOUL",5) in m.spell_cast_values
               for m in roster.models)


def test_azogs_hunters_production_fixture_loads(real_armies):
    _,(azog,_)=real_armies
    roster=collect_real_army_roster("hunters",azog)
    assert roster.total_points==azog.total_points()
    assert roster.models


def test_multiple_copies_receive_distinct_id(real_armies):
    _,(azog,_)=real_armies
    roster=collect_real_army_roster("hunters",azog)
    assert len({m.model_id for m in roster.models})==len(roster.models)


def test_selected_options_retained(real_armies):
    _,(azog,_)=real_armies
    roster=collect_real_army_roster("hunters",azog)
    configured_entries=[e for e in azog.entries
                        if e.counts_as_model and e.configured_profile.selected_options]
    assert configured_entries
    assert any(m.configured_option_ids for m in roster.models)


def test_hero_resource_values_match_real_entry(real_armies):
    (rise,_),_=real_armies
    roster=collect_real_army_roster("rise",rise)
    for i,entry in enumerate(rise.entries):
        if not entry.counts_as_model:
            continue
        selected=next(m for m in roster.models if m.model_id==f"rise:entry{i}:copy0")
        assert selected.might==entry.get_attribute("might")
        assert selected.will==entry.get_attribute("will")
        assert selected.fate==entry.get_attribute("fate")


def test_roster_has_no_elimination_probability_or_scoring(real_armies):
    (rise,_),_=real_armies
    roster=collect_real_army_roster("rise",rise)
    assert roster.dashboard_score is None
    assert roster.scenario_score is None
    assert not hasattr(roster,"elimination_probability")


def test_separate_armies_have_separate_model_ids(real_armies):
    (rise,_),(azog,_)=real_armies
    a=collect_real_army_roster("rise",rise)
    b=collect_real_army_roster("hunters",azog)
    assert set(m.model_id for m in a.models).isdisjoint(
        m.model_id for m in b.models)


def test_empty_army_has_no_invented_threat():
    r=collect_real_army_roster("empty",Army())
    assert r.models==() and r.total_points==0


def test_bad_army_rejected():
    with pytest.raises(TypeError,match="Army"):
        collect_real_army_roster("test",object())


def test_blank_label_rejected():
    with pytest.raises(ValueError,match="label"):
        collect_real_army_roster(" ",Army())


def test_label_does_not_change_profile_data(real_armies):
    (rise,_),_=real_armies
    a=collect_real_army_roster("A",rise)
    b=collect_real_army_roster("B",rise)
    assert [m.profile_id for m in a.models]==[m.profile_id for m in b.models]


def test_fixture_does_not_modify_production_army(real_armies):
    (rise,_),_=real_armies
    before=rise.total_points()
    collect_real_army_roster("rise",rise)
    assert rise.total_points()==before

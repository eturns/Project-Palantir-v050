"""DEV-077-GUN-B1: Gundabad-only option registrations, no runtime rule claims."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def read(relative):
    with (DATA / relative).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


EXPECTED = {
    'OPT0668': ('AZOG_THE_DEFILER', 15),
    'OPT0669': ('AZOG_THE_DEFILER', 10),
    'OPT0670': ('BOLG_SPAWN_OF_AZOG', 20),
    'OPT0671': ('BOLG_SPAWN_OF_AZOG', 5),
    'OPT0672': ('GUNDABAD_ORC_WARRIOR', 26),
    'OPT0673': ('GUNDABAD_ORC_WARRIOR', 25),
    'OPT0674': ('GUNDABAD_ORC_WARRIOR', 1),
    'OPT0675': ('GUNDABAD_ORC_WARRIOR', 1),
    'OPT0676': ('GUNDABAD_BERSERKER', 1),
    'OPT0677': ('GUNDABAD_TROLL', 10),
}


def test_all_ten_external_ids_unique_and_correct():
    options = read('profiles/profile_options.csv')
    ids = [row['external_id'] for row in options if row['external_id']]
    assert len(ids) == len(set(ids)), 'external IDs must be unique across army lists'
    mapped = {row['external_id']: row for row in options}
    for external_id, (profile_id, points) in EXPECTED.items():
        assert mapped[external_id]['profile_id'] == profile_id
        assert int(mapped[external_id]['points']) == points


def test_gundabad_warrior_choice_required_and_mutually_exclusive():
    options = {row['external_id']: row for row in read('profiles/profile_options.csv')}
    group = {options[f'OPT067{i}']['exclusive_group'] for i in range(2, 6)}
    assert group == {'GUNDABAD_ORC_WARRIOR_EQUIPMENT'}
    assert all(options[f'OPT067{i}']['required_group'] == 'TRUE' for i in range(2, 6))
    assert options['OPT0676']['required_group'] == ''


def test_wargear_actions_include_troll_exchange():
    options = {row['external_id']: row['id'] for row in read('profiles/profile_options.csv')}
    assignments = read('profiles/profile_option_wargear.csv')
    actual = {(r['option_id'], r['wargear_id'], r['action']) for r in assignments}
    for external, wargear in [
        ('OPT0668', 'WG_STONE_FLAIL'), ('OPT0669', 'WG_HEAVY_ARMOUR'),
        ('OPT0671', 'WG_ORC_BOW'), ('OPT0672', 'WG_BANNER'),
        ('OPT0672', 'WG_SHIELD'), ('OPT0673', 'WG_BANNER'),
        ('OPT0674', 'WG_SHIELD'), ('OPT0675', 'WG_SPEAR'),
        ('OPT0676', 'WG_TWO_HANDED_WEAPON'),
        ('OPT0677', 'WG_SCYTHE_GAUNTLETS'),
    ]:
        assert (options[external], wargear, 'grant') in actual
    assert (options['OPT0677'], 'WG_CRUSHING_CLUB', 'remove') in actual


def test_bolg_fell_warg_mount_linked():
    options = {row['external_id']: row['id'] for row in read('profiles/profile_options.csv')}
    links = {(r['option_id'], r['mount_id']) for r in read('profiles/profile_option_mount.csv')}
    assert (options['OPT0670'], 'MOUNT_FELL_WARG') in links


def test_new_wargear_ids_are_registered():
    ids = {r['id'] for r in read('wargear/wargear.csv')}
    assert {'WG_STONE_FLAIL', 'WG_SCYTHE_GAUNTLETS', 'WG_CRUSHING_CLUB'} <= ids


def test_existing_army_external_ids_and_links_retained():
    ids = {r['external_id'] for r in read('profiles/profile_options.csv')}
    assert {'OPT0682', 'OPT0683', 'OPT0684', 'OPT0685', 'OPT0690', 'OPT0691', 'OPT0692'} <= ids


def test_azog_armour_is_registered_but_legality_not_silently_approved():
    """The Gundabad army list REQUIRES heavy armour, unlike generic Azog."""
    options = {r['external_id']: r for r in read('profiles/profile_options.csv')}
    assert int(options['OPT0669']['points']) == 10
    assert options['OPT0669']['required_group'] == ''
    # Enforce this in the GUN-D army-list construction service, not global Azog options.

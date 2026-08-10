# Armies of The Hobbit Representative Validation Matrix

## Purpose

This matrix records the representative profiles and configurations used
to validate Project Palantír's normalized data architecture before
book-wide profile entry begins.

DEV-043A validates data identity and relationships. It does not require
the complete battlefield behaviour of every represented mechanic.

## Current validation coverage

| Validation case | Representative profile or configuration | Evidence currently validated | Status |
|---|---|---|---|
| Basic infantry | Iron Hills Warrior | Base statistics, points and default wargear load from canonical Profile data | Complete |
| Hero | Iron Hills Captain | Hero profile statistics, points and heroic resources load correctly | Complete |
| Named Hero | Dáin Ironfoot, Lord of the Iron Hills | Named profile identity, statistics, points and heroic resources load correctly | Complete |
| Default wargear | Iron Hills Warrior | Heavy armour and hand weapon resolve from Profile default wargear | Complete |
| Banner configuration | Iron Hills Warrior with Banner | Banner resolves as selected wargear without creating a duplicate Profile | Complete |
| Combined wargear option | Iron Hills Warrior with Banner and Shield | A single ProfileOption grants the complete purchased equipment package | Complete |
| Purchased equipment option | Iron Hills Warrior with Crossbow | Crossbow option resolves and increases configured points correctly | Complete |
| Wargear exchange | Iron Hills Captain with Mattock | Shield and spear are removed and Mattock is granted | Complete |
| Wargear exchange on cavalry | Iron Hills Goat Rider with Mattock | War spear is removed and Mattock is granted while the inherent mount remains | Complete |
| Inherent mount | Iron Hills Goat Rider | War Goat resolves from Profile.default_mount without requiring a selected option | Complete |
| Optional mount | Dáin on War Boar | War Boar resolves through a selected ProfileOption and configured points increase correctly | Complete |
| Optional platform | Iron Hills Captain on Iron Hills Chariot | Chariot resolves as an optional Platform rather than Wargear or Mount | Complete |
| Separate platform profile | Iron Hills Chariot | Chariot profile loads independently with its own statistics, points and default wargear | Complete |
| Repeated identical configuration | Two Iron Hills Warriors with Crossbows | Identical Profile and option combinations group into one configured entry with quantity 2 | Complete |
| Distinct configurations of one Profile | Iron Hills Warrior variants | Banner, Banner and Shield, Shield and Spear, Crossbow and Mattock remain separate configured entries | Complete |
| Real JSON import | Supplied Iron Hills roster | Army list, profiles, external option IDs and quantities import without flattening configurations | Complete |
| Configured roster points | Supplied Iron Hills roster | Imported configured entries reproduce the complete roster total of 823 points | Complete |
| Support model | Not yet selected | A representative battlefield-support profile or relationship must be added | Remaining |
| Second faction | Not yet selected | At least one non-Iron-Hills profile must validate that the architecture is faction-independent | Remaining |

## Architecture demonstrated

The current Iron Hills validation set demonstrates:

- one canonical Profile for each model;
- reusable Wargear objects;
- ProfileOption packages;
- Wargear grant and removal assignments;
- inherent and optional Mount relationships;
- optional Platform relationships;
- external model and option ID mapping;
- configured-profile point calculation;
- quantity-preserving JSON import;
- grouping by Profile and selected option set.

## Deferred battlefield behaviour

The following mechanics are represented structurally but their complete
battlefield behaviour belongs to later development tickets:

- cavalry charge bonuses;
- Knock Down;
- rider and mount targeting;
- dismounting;
- chariot movement and impact hits;
- Rapid-fire Bolt Thrower behaviour;
- siege-engine operation;
- battlefield support contributions;
- special-rule combat effects.

## DEV-043A remaining validation gaps

DEV-043A still requires:

1. one representative support-model case;
2. one representative profile from a second faction;
3. dataset-level completeness tests;
4. consolidated source references;
5. final regression and closure documentation.
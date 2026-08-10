# Armies of The Hobbit Validation Source References

## Purpose

This document records the primary rulebook evidence used by the
DEV-043A representative validation dataset.

The validation dataset checks profile identity, statistics, points,
wargear, options, mounts, platforms and configuration relationships.

Complete battlefield behaviour remains assigned to later combat-engine
tickets.

## Primary source

**Middle-earth Strategy Battle Game: Armies of The Hobbit (2024)**

## Representative profiles

### Dáin Ironfoot, Lord of the Iron Hills

- Profile ID: `IH_DAIN`
- Faction: Iron Hills
- Source page: 27
- Base points: 160
- Optional War Boar: 25 points
- Validation cases:
  - named Hero;
  - Heroic resources;
  - optional Mount;
  - configured points.

The source presents Dáin at 160 points and gives the War Boar its own
Mount profile. :contentReference[oaicite:0]{index=0}

### Iron Hills Captain

- Profile ID: `IH_CAP`
- Faction: Iron Hills
- Source page: 28
- Base points: 80
- Default wargear:
  - heavy armour;
  - shield;
  - spear;
  - hand weapon.
- Options:
  - Iron Hills Chariot: 170 points;
  - exchange shield and spear for Mattock: free.
- Validation cases:
  - Hero;
  - optional Platform;
  - wargear exchange;
  - ProfileOption removal and grant assignments.

The profile and both options appear together on page 28. :contentReference[oaicite:1]{index=1}

### Iron Hills Warrior

- Profile ID: `IH_WR`
- Faction: Iron Hills
- Source page: 29
- Base points: 10
- Default wargear:
  - heavy armour;
  - hand weapon.
- Required equipment options:
  - Banner and shield: 26 points;
  - Banner: 25 points;
  - Shield and spear: 2 points;
  - Crossbow: 2 points;
  - Mattock: 1 point.
- Validation cases:
  - basic infantry;
  - default wargear;
  - banner configuration;
  - support-capable spear configuration;
  - purchased wargear;
  - distinct configurations of one Profile;
  - repeated configured quantity.

The Warrior profile, default wargear and equipment choices are recorded
on page 29. :contentReference[oaicite:2]{index=2}

### Iron Hills Goat Rider

- Profile ID: `IH_GR`
- Faction: Iron Hills
- Source page: 30
- Base points: 20
- Default relationship:
  - Iron Hills Goat as inherent Mount.
- Default wargear:
  - heavy armour;
  - war spear;
  - hand weapon.
- Option:
  - exchange war spear for Mattock: free.
- Validation cases:
  - cavalry;
  - inherent Mount;
  - cavalry wargear exchange;
  - retaining a default Mount after equipment changes.

The source identifies the Goat Rider as Cavalry and records the free
Mattock exchange. :contentReference[oaicite:3]{index=3}

### Iron Hills Chariot

- Profile ID: `IH_CHARIOT`
- Faction: Iron Hills
- Source page: 32
- Base points: 170
- Profile:
  - Movement 8";
  - Fight 4;
  - Shoot 4+;
  - Strength 4;
  - Defence 8;
  - Attacks 2;
  - Wounds 4;
  - Courage 6+;
  - Intelligence 6+.
- Default wargear:
  - heavy armour;
  - hand weapon;
  - Rapid-fire Bolt Thrower.
- Validation cases:
  - independent Platform profile;
  - Platform statistics;
  - Platform default wargear;
  - Captain-to-Platform option relationship.

The source presents the Chariot as a Warrior, Chariot profile with its
own characteristics. :contentReference[oaicite:4]{index=4}

### Sauron, the Necromancer

- Profile ID: `DG_NEC`
- Faction: Dol Guldur
- Source page: 129
- Base points: 200
- Validation cases:
  - second faction;
  - non-Iron-Hills profile;
  - profile without selected options;
  - reuse of the normalized `ConfiguredProfile` architecture.

The source lists Sauron, the Necromancer at 200 points on page 129. :contentReference[oaicite:5]{index=5}

## Army-list option evidence

The Iron Hills army-list summary records:

- Dáin: 160 points;
- War Boar: 25 points;
- Captain: 80 points;
- Captain's Chariot: 170 points;
- Captain's Mattock exchange: free;
- Warrior: 10 points;
- Warrior equipment prices;
- Goat Rider: 20 points;
- Goat Rider's Mattock exchange: free;
- Chariot: 170 points.

This provides an independent points-and-options check against the
individual profile pages. :contentReference[oaicite:6]{index=6}

## Imported roster evidence

The supplied Iron Hills JSON export is retained unchanged at:

```text
tests/fixtures/iron_hills_army.json
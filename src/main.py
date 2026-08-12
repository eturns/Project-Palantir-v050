"""
Project Palantír
================

Main entry point.
"""
import json
import sys
from loader import load_all_profiles
from rule_loader import (
    load_special_rules,
    load_heroic_actions,
    load_spells,
    load_ability_tags,
    load_ability_prerequisites,
)

from relationship_loader import (
    load_profile_special_rules,
    load_profile_heroic_actions,
    load_profile_spells,
    load_heroic_action_tags,
    load_special_rule_tags,
    load_spell_tags,
    load_heroic_action_prerequisites,
    load_special_rule_prerequisites,
    load_spell_prerequisites,
    load_army_rule_tags
)

from queries import total_points
from validation_runner import run_validation

from analysis_loader import (
    load_metric_thresholds,
    load_metric_descriptions
)
from army_loader import (
    load_factions,
    load_army_lists,
    load_army_rules
)


from services import (
    analyse_mesbg_list_builder_file,
)

from reporting import (
    print_text_analysis_report,
)
from file_selection import (
    select_mesbg_json_file,
)
from pathlib import Path
def main(
    file_path: str,
):
    """
    Main entry point for Project Palantír.
    """

    print("Project Palantír Initialised")
    print()
    path = Path(
        file_path,
    )

    if not path.exists():
        print(
            "Unable to open army file:"
         )
        print(
            file_path,
        )
        print()
        print(
            "Please select an existing MESBG List Builder "
            "JSON file."
        )
        return

    # ==========================================================
    # Load database
    # ==========================================================

    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    database_points = total_points(profiles)
   
    factions = load_factions()

    army_lists = load_army_lists(
        factions,
    )

    army_rules = load_army_rules(
        army_lists,
    )
    # ==========================================================
    # Load rule database
    # ==========================================================

    special_rules = load_special_rules()
    heroic_actions = load_heroic_actions()
    spells = load_spells()
    ability_tags = load_ability_tags()
    ability_prerequisites = load_ability_prerequisites()

    # ==========================================================
    # Load analysis database
    # ==========================================================
    
    metric_thresholds = load_metric_thresholds()
    metric_descriptions = load_metric_descriptions()

    # ==========================================================
    # Load relationships
    # ==========================================================

    load_profile_special_rules(
        profiles_by_id,
        special_rules,
    )

    load_profile_heroic_actions(
        profiles_by_id,
        heroic_actions,
    )

    load_profile_spells(
        profiles_by_id,
        spells,
    )

    load_special_rule_tags(
        special_rules,
        ability_tags,
    )

    load_heroic_action_tags(
        heroic_actions,
        ability_tags,
    )

    load_spell_tags(
        spells,
        ability_tags,
    )

    load_army_rule_tags(
        army_rules,
        ability_tags,
    )
    load_heroic_action_prerequisites(
        heroic_actions,
        ability_prerequisites,
    )

    load_spell_prerequisites(
        spells,
        ability_prerequisites,
    )

    load_special_rule_prerequisites(
        special_rules,
        ability_prerequisites,
    )

    # ==========================================================
    # Analyse imported MESBG List Builder file
    # ==========================================================
    try:
        result = analyse_mesbg_list_builder_file(
            str(path),
            profiles_by_id,
            army_lists,
        metric_thresholds,
        )
    except json.JSONDecodeError:
        print(
            "Unable to read army file."
        )
        print()
        print(
            "The selected file is not valid JSON."
        )
        return

    except ValueError as error:
        print(
            "Unable to import army file."
        )
        print()
        print(
            str(error)
        )
        return

    except OSError as error:
        print(
            "Unable to open army file."
        )
        print()
        print(
            str(error)
        )
        return

    print_text_analysis_report(
        result,
    )
   
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        file_path = sys.argv[1]
    else:
        file_path = select_mesbg_json_file()

    if file_path is None:
        print("No army file selected.")
        sys.exit(0)


    main(
        file_path,
    )
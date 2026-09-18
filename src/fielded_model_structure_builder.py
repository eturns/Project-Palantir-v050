from fielded_model import FieldedModel
from fielded_model_relationship import (
    FieldedModelRelationship,
)
from fielded_model_relationship_set import (
    FieldedModelRelationshipSet,
)
from fielded_model_structure_definition import (
    FieldedModelStructureDefinition,
)
from profiles import Profile


def build_fielded_model_structures(
    fielded_models: tuple[FieldedModel, ...],
    structure_definitions: dict[
        str,
        FieldedModelStructureDefinition,
    ],
    profiles_by_id: dict[str, Profile],
) -> FieldedModelRelationshipSet:
    relationships = []

    option_structured_model_ids: set[str] = set()

    for source_model in fielded_models:
        configured_profile = source_model.configured_profile

        if configured_profile is None:
            continue

        for option in configured_profile.selected_options:
            for assignment in option.profile_assignments:
                if assignment.relationship_type is None:
                    continue

                matching_models = tuple(
                    model
                    for model in fielded_models
                    if (
                        model.id != source_model.id
                        and model.id
                        not in option_structured_model_ids
                        and model.warband_id
                        == source_model.warband_id
                        and model.profile_id
                        == assignment.profile_id
                    )
                )

                if not matching_models:
                    raise ValueError(
                        "Expected an available fielded model "
                        "for option-assigned Profile ID "
                        f"'{assignment.profile_id}' in warband "
                        f"'{source_model.warband_id}'."
                    )

                target_model = matching_models[0]

                option_structured_model_ids.add(
                    target_model.id
                )

                relationships.append(
                    FieldedModelRelationship(
                        source_fielded_model_id=(
                            source_model.id
                        ),
                        target_fielded_model_id=(
                            target_model.id
                        ),
                        relationship_type=(
                            assignment.relationship_type
                        ),
                    )
                )

    for root_model in fielded_models:
        root_profile_id = root_model.profile_id

        definition = structure_definitions.get(
            root_profile_id
        )
        if root_model.id in option_structured_model_ids:
            continue

        if definition is None:
            continue

        structural_member_ids: set[str] = set()

        for member in definition.members:
            if member.profile_id not in profiles_by_id:
                raise ValueError(
                    "Unknown structure member Profile ID "
                    f"'{member.profile_id}'."
                )

            matching_models = tuple(
                model
                for model in fielded_models
                if (
                    model.id != root_model.id
                    and model.id not in structural_member_ids
                    and model.warband_id
                    == root_model.warband_id
                    and model.profile_id == member.profile_id
                )
            )

            if not matching_models:
                raise ValueError(
                    "Expected an available fielded structure "
                    f"member with Profile ID "
                    f"'{member.profile_id}' in warband "
                    f"'{root_model.warband_id}'."
                )

            member_model = matching_models[0]

            structural_member_ids.add(
                member_model.id
            )

            relationships.append(
                FieldedModelRelationship(
                    source_fielded_model_id=(
                        member_model.id
                    ),
                    target_fielded_model_id=(
                        root_model.id
                    ),
                    relationship_type=(
                        member.relationship_type
                    ),
                )
            )

        if (
            definition
            .warband_member_relationship_type
            is not None
            and root_model.warband_id is not None
        ):
            for candidate_model in fielded_models:
                if candidate_model.id == root_model.id:
                    continue

                if (
                    candidate_model.id
                    in structural_member_ids
                ):
                    continue

                if (
                    candidate_model.warband_id
                    != root_model.warband_id
                ):
                    continue

                relationships.append(
                    FieldedModelRelationship(
                        source_fielded_model_id=(
                            candidate_model.id
                        ),
                        target_fielded_model_id=(
                            root_model.id
                        ),
                        relationship_type=(
                            definition
                            .warband_member_relationship_type
                        ),
                    )
                )

    return FieldedModelRelationshipSet(
        fielded_models=fielded_models,
        relationships=tuple(relationships),
    )
"""Materials router with handlers implementation."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from starlette import status

import dependencies
import models
from repositories import RepositoryException

router = APIRouter(prefix="/materials")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=models.MaterialResponse,
)
async def create_material(
    repository: dependencies.MaterialRepository,
    session: dependencies.DBSession,
    material: models.MaterialCreate,
) -> models.MaterialResponse:
    """Create a new material and persist it to the database.

    This function handles the creation and registration of a new material
    instance into the database session. If the material already exists
    based on database constraints, for example, unique constraints, an
    HTTP 409 conflict is raised. Otherwise, the newly created material
    will be committed to the database and returned.

    :param repository: Material repository used for persistence operations for
        materials.
    :param session: Database session used for interacting with underlying
        storage for commit and persist operations.
    :type session: dependencies.DBSession
    :param material: Instance of the `Material` model with the required
        data to create a new material in the system.
    :type material: models.Material
    :return: Newly created material model object as persistent data within the
        database.
    :rtype: models.MaterialResponse
    :raises HTTPException: Raised with status code 409 (Conflict) if
        there is an integrity error during the creation process,
        such as a duplicate entry.
    """
    repository.use_session(session)
    try:
        record = models.Material(**material.model_dump(mode="sql", exclude_unset=True))
        repository.create(record)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    else:
        session.commit()
        return models.MaterialResponse.model_validate(record, from_attributes=True)


@router.get(
    "/",
    response_model=list[models.MaterialResponse],
    response_model_exclude={"__all__": ("created_at", "boms", "products", "stock")},
)
async def list_materials(
    repository: dependencies.MaterialRepository,
    session: dependencies.DBSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0, le=1000)] = 1000,
) -> list[models.MaterialResponse]:
    """Fetch a paginated list of materials from the database.

    Retrieves a paginated list of materials from the database based on the
    specified offset and limit.

    :param repository: Material repository used for persistence operations for
        materials.
    :param session: Database session used to execute queries.
    :type session: dependencies.DBSession
    :param offset: Number of materials to skip in the query result.
        Defaults to 0.
    :type offset: int
    :param limit: Maximum number of materials to retrieve in the query result.
        Values greater than 100 are not allowed. Defaults to 100.
    :type limit: int
    :return: A list of materials retrieved based on the offset and limit.
    :rtype: list[models.Material]
    """
    repository.use_session(session)
    materials = repository.list_paginated(offset, limit)
    session.rollback()
    return [
        models.MaterialResponse.model_validate(material, from_attributes=True)
        for material in materials
    ]


@router.get(
    "/{slug}",
    response_model=models.MaterialResponse,
    response_model_exclude={
        "boms": {
            "__all__": (
                "material_id",
                "material_name",
                "material_slug",
                "product_id",
            ),
        },
        "stock": {
            "__all__": (
                "material_id",
                "material_name",
                "material_slug",
                "warehouse_idF",
            ),
        },
    },
)
async def get_material(
    repository: dependencies.MaterialRepository,
    session: dependencies.DBSession,
    slug: str,
) -> models.MaterialResponse:
    """Retrieve a material by its slug from the database.

    This function fetches a material record from the database using the
    provided slug and returns it. If a material with the specified slug does
    not exist, an HTTP 404 error is raised.

    :param repository: Material repository used for persistence operations for
        materials.
    :param session: A database session dependency for querying the database.
    :type session: dependencies.DBSession
    :param slug: The slug of the material to retrieve.
    :type slug: str
    :return: The material object matching the specified slug.
    :rtype: models.Material
    :raises HTTPException: If no material is found with the given slug.
    """
    repository.use_session(session)
    try:
        material = repository.find_by_slug(slug)
    except RepositoryException as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail="Material not found") from exc
    else:
        session.rollback()
        return models.MaterialResponse.model_validate(material, from_attributes=True)


@router.patch(
    "/{slug}",
    response_model=models.MaterialResponseSimple,
)
async def update_material(
    repository: dependencies.MaterialRepository,
    session: dependencies.DBSession,
    slug: str,
    new_material: models.MaterialPatch,
) -> models.MaterialResponseSimple:
    """Update the properties of an existing material in the database.

    This function retrieves a material by its slug from the database and
    updates its attributes based on the provided input. The function ensures
    that the database row is locked during the update
    process to avoid conflicts. Any changes made are committed, and the updated
    material is returned.

    :param repository: Material repository used for persistence operations for
        materials.
    :param session: The database session used to interact with the database.
    :param slug: The unique identifier for the material to update.
    :param new_material: Object containing the updated properties of the
        material.
    :return: The updated material object.
    """
    repository.use_session(session)
    try:
        material = repository.find_by_slug(slug)
    except RepositoryException as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        ) from exc

    do_update = False
    if new_material.quantity_unit is not None:
        material.quantity_unit = new_material.quantity_unit
        do_update = True

    if do_update:
        repository.update(material)

    session.commit()
    return models.MaterialResponseSimple.model_validate(material, from_attributes=True)


@router.delete(
    "/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_material(
    repository: dependencies.MaterialRepository,
    session: dependencies.DBSession,
    slug: str,
) -> None:
    """Delete a material from the database given its slug.

    This function is designed to handle HTTP DELETE requests, deleting
    a material identified by its slug from the database if it exists.
    If the specified material does not exist, an HTTP 404 not found
    exception is raised.

    :param repository: Material repository used for persistence operations for
        materials.
    :param session: Database session used for executing database queries.
    :type session: dependencies.DBSession
    :param slug: Name of the material to be deleted.
    :type slug: str
    :return: This function does not return a value.
    :rtype: None
    :raises HTTPException: If the material with the specified slug is not found.
    """
    repository.use_session(session)
    try:
        material = repository.find_by_slug(slug)
    except RepositoryException as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        ) from exc

    repository.delete(material)
    session.commit()

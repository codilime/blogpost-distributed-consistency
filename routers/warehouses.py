"""Warehouses router with handlers implementation."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from starlette import status

import dependencies
import models
from repositories import RepositoryException

router = APIRouter(prefix="/warehouses")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=models.WarehouseResponse,
)
async def create_warehouse(
    repository: dependencies.WarehouseRepository,
    session: dependencies.DBSession,
    warehouse: models.WarehouseCreate,
) -> models.WarehouseResponse:
    """Create a new warehouse and persist it to the database.

    This function handles the creation and registration of a new warehouse
    instance into the database session. If the warehouse already exists
    based on database constraints, for example, unique constraints, an
    HTTP 409 conflict is raised. Otherwise, the newly created warehouse
    will be committed to the database and returned.

    :param repository: Product repository used for persistence operations for
        products.
    :type repository: repositories.WarehouseRepository
    :param session: Database session used for interacting with underlying
        storage for commit and persist operations.
    :type session: dependencies.DBSession
    :param warehouse: Instance of the `Warehouse` model with the required
        data to create a new warehouse in the system.
    :type warehouse: models.Warehouse
    :return: Newly created warehouse model object as persistent data within the
        database.
    :rtype: models.WarehouseResponse
    :raises HTTPException: Raised with status code 409 (Conflict) if
        there is an integrity error during the creation process,
        such as a duplicate entry.
    """
    repository.use_session(session)
    try:
        record = models.Warehouse(**warehouse.model_dump(mode="sql", exclude_unset=True))
        if warehouse.max_capacity is not None:
            record.max_capacity = warehouse.max_capacity
        repository.create(record)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    else:
        session.commit()
        return models.WarehouseResponse.model_validate(record, from_attributes=True)


@router.get(
    "/",
    response_model=list[models.WarehouseResponse],
    response_model_exclude={"__all__": ("id", "created_at", "stock", "products")},
)
async def list_warehouses(
    repository: dependencies.WarehouseRepository,
    session: dependencies.DBSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0, le=1000)] = 1000,
) -> list[models.WarehouseResponse]:
    """Fetch a paginated list of warehouses from the database.

    Retrieves a paginated list of warehouses from the database based on the
    specified offset and limit.

    :param repository: Warehouse repository used for persistence operations for
        warehouses.
    :type repository: repositories.WarehouseRepository
    :param session: Database session used to execute queries.
    :type session: dependencies.DBSession
    :param offset: Number of warehouses to skip in the query result.
        Defaults to 0.
    :type offset: int
    :param limit: Maximum number of warehouses to retrieve in the query result.
        Values greater than 100 are not allowed. Defaults to 100.
    :type limit: int
    :return: A list of warehouses retrieved based on the offset and limit.
    :rtype: list[models.Warehouse]
    """
    repository.use_session(session)
    warehouses = repository.list_paginated(offset, limit)
    return [
        models.WarehouseResponse.model_validate(warehouse, from_attributes=True)
        for warehouse in warehouses
    ]


@router.get(
    "/{slug}",
    response_model=models.WarehouseResponse,
    response_model_exclude={
        "stock": {
            "__all__": (
                "material_id",
                "warehouse_id",
                "warehouse_name",
                "warehouse_slug",
            ),
        },
    },
)
async def get_warehouse(
    repository: dependencies.WarehouseRepository,
    session: dependencies.DBSession,
    slug: str,
) -> models.WarehouseResponse:
    """Retrieve a warehouse by its slug from the database.

    This function fetches a warehouse record from the database using the
    provided slug and returns it. If a warehouse with the specified slug does
    not exist, an HTTP 404 error is raised.

    :param repository: Warehouse repository used for persistence operations for
        warehouses.
    :type repository: repositories.WarehouseRepository
    :param session: A database session dependency for querying the database.
    :type session: dependencies.DBSession
    :param slug: The slug of the warehouse to retrieve.
    :type slug: str
    :return: The warehouse object matching the specified slug.
    :rtype: models.Warehouse
    :raises HTTPException: If no warehouse is found with the given slug.
    """
    repository.use_session(session)
    try:
        warehouse = repository.find_by_slug(slug)
    except RepositoryException as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    else:
        session.rollback()
        return models.WarehouseResponse.model_validate(warehouse, from_attributes=True)


@router.patch(
    "/{slug}",
    response_model=models.WarehouseResponseSimple,
)
async def update_warehouse(
    repository: dependencies.WarehouseRepository,
    session: dependencies.DBSession,
    slug: str,
    new_warehouse: models.WarehousePatch,
) -> models.WarehouseResponseSimple:
    """Update the properties of an existing warehouse in the database.

    This function retrieves a warehouse by its slug from the database and
    updates its attributes based on the provided input. The function ensures
    that the database row is locked during the update
    process to avoid conflicts. Any changes made are committed, and the updated
    warehouse is returned.

    :param repository: Warehouse repository used for persistence operations for
        warehouses.
    :type repository: repositories.WarehouseRepository
    :param session: The database session used to interact with the database.
    :param slug: The unique identifier for the warehouse to update.
    :param new_warehouse: Object containing the updated properties of the
        warehouse.
    :return: The updated warehouse object.
    """
    repository.use_session(session)
    try:
        warehouse = repository.find_by_slug(slug)
    except RepositoryException as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    do_update = False
    if new_warehouse.location is not None:
        warehouse.location = new_warehouse.location
        do_update = True
    if new_warehouse.max_capacity is not None:
        warehouse.max_capacity = new_warehouse.max_capacity
        do_update = True

    if do_update:
        repository.update(warehouse)
        session.commit()
    else:
        session.rollback()

    return models.WarehouseResponseSimple.model_validate(warehouse, from_attributes=True)


@router.delete(
    "/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_warehouse(
    repository: dependencies.WarehouseRepository,
    session: dependencies.DBSession,
    slug: str,
) -> None:
    """Delete a warehouse from the database given its slug.

    This function is designed to handle HTTP DELETE requests, deleting
    a warehouse identified by its slug from the database if it exists.
    If the specified warehouse does not exist, an HTTP 404 not found
    exception is raised.

    :param repository: Warehouse repository used for persistence operations for
        warehouses.
    :type repository: repositories.WarehouseRepository
    :param session: Database session used for executing database queries.
    :type session: dependencies.DBSession
    :param slug: Name of the warehouse to be deleted.
    :type slug: str
    :return: This function does not return a value.
    :rtype: None
    :raises HTTPException: If the warehouse with the specified slug is not found.
    """
    repository.use_session(session)
    try:
        warehouse = repository.find_by_slug(slug)
    except RepositoryException as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    repository.delete(warehouse)
    session.commit()

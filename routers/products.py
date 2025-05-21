"""Products router with handlers implementation."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from starlette import status

import dependencies
import models
from repositories import RepositoryException

router = APIRouter(prefix="/products")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=models.ProductResponse,
)
async def create_product(
    repository: dependencies.ProductRepository,
    session: dependencies.DBSession,
    product: models.ProductCreate,
) -> models.ProductResponse:
    """Create a new product and persist it to the database.

    This function handles the creation and registration of a new product
    instance into the database session. If the product already exists
    based on database constraints, for example, unique constraints, an
    HTTP 409 conflict is raised. Otherwise, the newly created product
    will be committed to the database and returned.

    :param repository: Product repository used for persistence operations for
        products.
    :param session: Database session used for interacting with underlying
        storage for commit and persist operations.
    :type session: dependencies.DBSession
    :param product: Instance of the `Product` model with the required
        data to create a new product in the system.
    :type product: models.Product
    :return: Newly created product model object as persistent data within the
        database.
    :rtype: models.ProductResponse
    :raises HTTPException: Raised with status code 409 (Conflict) if
        there is an integrity error during the creation process,
        such as a duplicate entry.
    """
    repository.use_session(session)
    try:
        record = models.Product(**product.model_dump(mode="sql", exclude_unset=True))
        record = repository.create(record)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    else:
        session.commit()
        return models.ProductResponse.model_validate(record, from_attributes=True)


@router.get(
    "/",
    response_model=list[models.ProductResponse],
    response_model_exclude={"__all__": ("id", "created_at", "boms", "products")},
)
async def list_products(
    repository: dependencies.ProductRepository,
    session: dependencies.DBSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0, le=1000)] = 1000,
) -> list[models.ProductResponse]:
    """Fetch a paginated list of products from the database.

    Retrieves a paginated list of products from the database based on the
    specified offset and limit.

    :param repository: Product repository used for persistence operations for
        products.
    :param session: Database session used to execute queries.
    :type session: dependencies.DBSession
    :param offset: Number of products to skip in the query result.
        Defaults to 0.
    :type offset: int
    :param limit: Maximum number of products to retrieve in the query result.
        Values greater than 100 are not allowed. Defaults to 100.
    :type limit: int
    :return: A list of products retrieved based on the offset and limit.
    :rtype: list[models.Product]
    """
    repository.use_session(session)
    products = repository.list_paginated(offset, limit)
    session.rollback()
    return [
        models.ProductResponse.model_validate(product, from_attributes=True)
        for product in products
    ]


@router.get(
    "/{slug}",
    response_model=models.ProductResponse,
    response_model_exclude={
        "boms": {
            "__all__": (
                "material_id",
                "product_id",
                "product_name",
                "product_slug",
            ),
        },
    },
)
async def get_product(
    repository: dependencies.ProductRepository,
    session: dependencies.DBSession,
    slug: str,
) -> models.ProductResponse:
    """Retrieve a product by its slug from the database.

    This function fetches a product record from the database using the
    provided slug and returns it. If a product with the specified slug does
    not exist, an HTTP 404 error is raised.

    :param repository: Product repository used for persistence operations for
        products.
    :param session: A database session dependency for querying the database.
    :type session: dependencies.DBSession
    :param slug: The slug of the product to retrieve.
    :type slug: str
    :return: The product object matching the specified slug.
    :rtype: models.Product
    :raises HTTPException: If no product is found with the given slug.
    """
    repository.use_session(session)
    try:
        product = repository.find_by_slug(slug)
    except RepositoryException as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail="Product not found") from exc
    else:
        session.rollback()
        return models.ProductResponse.model_validate(product, from_attributes=True)


@router.patch(
    "/{slug}",
    response_model=models.ProductResponseSimple,
)
async def update_product(
    repository: dependencies.ProductRepository,
    session: dependencies.DBSession,
    slug: str,
    new_product: models.ProductPatch,
) -> models.ProductResponseSimple:
    """Update the properties of an existing product in the database.

    This function retrieves a product by its slug from the database and
    updates its attributes based on the provided input. The function ensures
    that the database row is locked during the update
    process to avoid conflicts. Any changes made are committed, and the updated
    product is returned.

    :param repository: Product repository used for persistence operations for
        products.
    :param session: The database session used to interact with the database.
    :param slug: The unique identifier for the product to update.
    :param new_product: Object containing the updated properties of the
        product.
    :return: The updated product object.
    """
    repository.use_session(session)
    try:
        product = repository.find_by_slug(slug)
    except RepositoryException as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        ) from exc

    do_update = False
    # TODO (mateumann): add some reasonable functionality

    if do_update:
        repository.update(product)

    session.commit()
    return models.ProductResponseSimple.model_validate(product, from_attributes=True)


@router.delete(
    "/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_product(
    repository: dependencies.ProductRepository,
    session: dependencies.DBSession,
    slug: str,
) -> None:
    """Delete a product from the database given its slug.

    This function is designed to handle HTTP DELETE requests, deleting
    a product identified by its slug from the database if it exists.
    If the specified product does not exist, an HTTP 404 not found
    exception is raised.

    :param repository: Product repository used for persistence operations for
        products.
    :param session: Database session used for executing database queries.
    :type session: dependencies.DBSession
    :param slug: Name of the product to be deleted.
    :type slug: str
    :return: This function does not return a value.
    :rtype: None
    :raises HTTPException: If the product with the specified slug is not found.
    """
    repository.use_session(session)
    try:
        product = repository.find_by_slug(slug)
    except RepositoryException as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        ) from exc

    repository.delete(product)
    session.commit()

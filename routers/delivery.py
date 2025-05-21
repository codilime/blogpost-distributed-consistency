"""Delivery router with handler implementation."""

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from starlette import status

import dependencies
import models
from repositories import RepositoryException

router = APIRouter(prefix="/delivery")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=models.WarehouseResponse,
)
async def create(
    warehouse_repository: dependencies.WarehouseRepository,
    stock_position_repository: dependencies.StockPositionRepository,
    session: dependencies.DBSession,
    delivery: models.Delivery,
) -> models.WarehouseResponse:
    """Handle the creation of a delivery and updates warehouse stock levels accordingly.

    This function is responsible for saving a new delivery record in the database and
    updating the stock levels of materials in the associated warehouse.
    If the material does not already exist in the stock positions, a new stock position
    is created. If it exists, the stock level is updated by adding the respective
    quantity from the delivery. The operation is conducted as a nested transaction
    to maintain database consistency. In the case of conflicting operations
    or other unexpected errors, appropriate HTTP responses are returned.

    :param warehouse_repository: Warehouse repository used for persistence operations for
        warehouses.
    :type warehouse_repository: repositories.WarehouseSQLRepository
    :param stock_position_repository: Stock position repository used for persistence operations for
        stock positions.
    :type stock_position_repository: repositories.StockPositionSQLRepository
    :param session: Database session object used to interact with the database.
    :type session: dependencies.DBSession
    :param delivery: Delivery object containing details of the delivery and associated positions.
    :type delivery: models.Delivery
    :return: None
    :rtype: None
    :raises HTTPException: Raised with status 409 if integrity constraints are violated during execution.
    :raises HTTPException: Raised with status 500 in case of unexpected errors during execution.
    """
    warehouse_repository.use_session(session)
    stock_position_repository.use_session(session)
    try:
        warehouse = warehouse_repository.find_by_id(delivery.warehouse_id)
        for position in delivery.positions:
            if warehouse.capacity < position.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="delivery cannot be processed because "
                    "it exceeds current warehouse capacity",
                )
            try:
                stock = stock_position_repository.find_by_warehouse_id_and_material_id(
                    warehouse_id=warehouse.id,
                    material_id=position.material_id,
                )
                stock.quantity += position.quantity
                stock_position_repository.update(stock)
            except RepositoryException:
                stock = models.StockPosition(
                    warehouse_id=warehouse.id,
                    material_id=position.material_id,
                    quantity=position.quantity,
                )
                stock_position_repository.create(stock)
        session.commit()
        return models.WarehouseResponse.model_validate(warehouse, from_attributes=True)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except HTTPException:
        session.rollback()
        raise
    except Exception as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

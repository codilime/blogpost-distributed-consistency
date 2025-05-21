"""Application dependencies defined as annotated types."""

import typing as t

from fastapi import Depends
from sqlmodel import Session
from starlette.requests import Request

import repositories
from models import StockPosition


def get_session(request: Request) -> t.Generator[Session]:
    """Yield a database session scoped to the incoming HTTP request.

    This function initialises a new database session tied to the underlying
    database engine of the application associated with the provided request.
    It uses a context manager to ensure proper session lifecycle management,
    including handling session commits and rollbacks as necessary and closing
    the connection afterwards. This is particularly useful in web applications
    to handle database interactions within the scope of an individual request.

    :param request: The incoming HTTP request containing the application and its
                    associated database engine.
    :type request: fastapi.Request
    :return: A generator yielding a `Session` instance for database operations.
    :rtype: Generator[sqlmodel.Session]
    """
    with Session(request.app.db_engine) as session:
        yield session


def get_material_repository(request: Request) -> t.Generator[repositories.MaterialSQLRepository]:
    """Yield a material repository scoped to the incoming HTTP request.

    :param request: The incoming HTTP request containing the application and its
                    associated database engine.
    :type request: fastapi.Request
    :return: A generator yielding a `repositories.MaterialSQLRepository` instance for material persistence operations.
    :rtype: Generator[repositories.MaterialSQLRepository]
    """
    repository = repositories.MaterialSQLRepository()
    yield repository


def get_product_repository(request: Request) -> t.Generator[repositories.ProductSQLRepository]:
    """Yield a product repository scoped to the incoming HTTP request.

    :param request: The incoming HTTP request containing the application and its
                    associated database engine.
    :type request: fastapi.Request
    :return: A generator yielding a `repositories.ProductSQLRepository` instance for product persistence operations.
    :rtype: Generator[repositories.ProductSQLRepository]
    """
    repository = repositories.ProductSQLRepository()
    yield repository


def get_stock_position_repository(
    request: Request,
) -> t.Generator[repositories.StockPositionSQLRepository]:
    """Yield a stock position repository scoped to the incoming HTTP request.

    :param request: The incoming HTTP request containing the application and its
                    associated database engine.
    :type request: fastapi.Request
    :return: A generator yielding a `repositories.StockPositionSQLRepository` instance for stock position persistence operations.
    :rtype: Generator[repositories.StockPositionSQLRepository]
    """
    repository = repositories.StockPositionSQLRepository()
    yield repository


def get_warehouse_repository(request: Request) -> t.Generator[repositories.WarehouseSQLRepository]:
    """Yield a warehouse repository scoped to the incoming HTTP request.

    :param request: The incoming HTTP request containing the application and its
                    associated database engine.
    :type request: fastapi.Request
    :return: A generator yielding a `repositories.WarehouseSQLRepository` instance for warehouse persistence operations.
    :rtype: Generator[repositories.WarehouseSQLRepository]
    """
    repository = repositories.WarehouseSQLRepository()
    yield repository


DBSession = t.Annotated[
    Session,
    Depends(get_session),
]


MaterialRepository = t.Annotated[
    repositories.MaterialSQLRepository,
    Depends(get_material_repository),
]

ProductRepository = t.Annotated[
    repositories.ProductSQLRepository,
    Depends(get_product_repository),
]


StockPositionRepository = t.Annotated[
    repositories.StockPositionSQLRepository,
    Depends(get_stock_position_repository),
]

WarehouseRepository = t.Annotated[
    repositories.WarehouseSQLRepository,
    Depends(get_warehouse_repository),
]

"""Top-level functions for the Factory application."""

import typing as t
from contextlib import asynccontextmanager

import uvicorn

import app
from repositories import db
from routers import delivery_router, materials_router, products_router, warehouses_router


@asynccontextmanager
async def lifespan(application: app.FactoryApp) -> t.AsyncGenerator[None]:
    """Set up and manage the lifespan context of the application.

    It configures the database, populates it, and attaches the database engine
    to the application context. On exiting the lifespan, the database
    connection is disposed to free resources.

    :param application: The FastAPI application instance.
    :type application: app.FactoryApp
    :return: An asynchronous context manager handling the application lifespan.
    :rtype: AsyncGenerator
    """
    engine = db.setup()
    # db.populate(engine)
    application.db_engine = engine
    yield
    engine.dispose()


def create_application() -> app.FactoryApp:
    """Create and configures an instance of the FactoryApp application.

    This function initializes an application of type FactoryApp with a
    specified title. It also attaches the materials router to the
    application, extending its functionality with predefined routes.
    The application's lifespan configuration can be defined as needed.

    :return: An instance of FactoryApp with the configured title and
        attached 'materials' router.
    :rtype: app.FactoryApp
    """
    application = app.FactoryApp(title="Factory App", lifespan=lifespan)
    application.include_router(delivery_router)
    application.include_router(materials_router)
    application.include_router(products_router)
    application.include_router(warehouses_router)
    return application


def main() -> None:  # noqa: D103
    uvicorn.run("main:create_application", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()

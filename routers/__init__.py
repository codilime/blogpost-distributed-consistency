"""FastAPI router definitions for the Factory application."""

from routers.delivery import router as delivery_router
from routers.materials import router as materials_router
from routers.products import router as products_router
from routers.warehouses import router as warehouses_router

__all__ = [
    "delivery_router",
    "materials_router",
    "products_router",
    "warehouses_router",
]

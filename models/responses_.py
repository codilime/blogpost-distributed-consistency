"""Pydantic models for REST responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class ProductResponseSimple(BaseModel):
    """Pydantic model for a simplified product response."""

    name: str
    slug: str


class ProductResponse(ProductResponseSimple):
    """Pydantic model for a product response."""

    id: uuid.UUID
    created_at: datetime
    boms: list["BOMResponseSimple"] | None = None
    materials: list["MaterialResponseSimple"] | None = None


class MaterialResponseSimple(BaseModel):
    """Pydantic model for a simplified material response."""

    name: str
    slug: str
    quantity_unit: str


class MaterialResponse(MaterialResponseSimple):
    """Pydantic model for a material response."""

    id: uuid.UUID
    created_at: datetime
    boms: list["BOMResponseSimple"] | None = None
    stock: list["StockPositionResponseSimple"] | None = None
    products: list["ProductResponseSimple"] | None = None


class BOMResponseSimple(BaseModel):
    """Pydantic model for a simplified Bill of Materials (BOM) response."""

    id: uuid.UUID
    material_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    material_name: str | None
    material_slug: str | None
    product_name: str | None
    product_slug: str | None


class BOMResponse(BOMResponseSimple):
    """Pydantic model for a Bill of Materials (BOM) response."""

    created_at: datetime
    product: ProductResponse | None = None
    material: MaterialResponse | None = None


class WarehouseResponseSimple(BaseModel):
    """Pydantic model for a simplified warehouse response."""

    name: str
    slug: str
    location: str
    capacity: int
    max_capacity: int


class WarehouseResponse(WarehouseResponseSimple):
    """Pydantic model for a warehouse response."""

    id: uuid.UUID
    created_at: datetime
    stock: list["StockPositionResponseSimple"] | None = None


class StockPositionResponseSimple(BaseModel):
    """Pydantic model for a simplified stock position response."""

    id: uuid.UUID
    material_id: uuid.UUID
    warehouse_id: uuid.UUID
    quantity: int
    material_name: str | None
    material_slug: str | None
    warehouse_name: str | None
    warehouse_slug: str | None


class StockPositionResponse(StockPositionResponseSimple):
    """Pydantic model for a stock position response."""

    created_at: datetime
    material: MaterialResponse | None = None
    warehouse: WarehouseResponse | None = None

"""Pydantic models for request bodies."""
import uuid

from pydantic import BaseModel, Field


class MaterialCreate(BaseModel):
    """Pydantic model for a material post request body.

    :ivar name: The name of this warehouse.
    :type name: str
    :ivar quantity_unit: The unit of measurement for quantities associated with
        this material patch.
    :type quantity_unit: str
    """

    name: str = Field(min_length=2)
    quantity_unit: str = Field(min_length=1, max_length=40)


class MaterialPatch(BaseModel):
    """Pydantic model for a material patch request body.

    :ivar quantity_unit: The unit of measurement for quantities associated with
        this material patch.
    :type quantity_unit: str
    """

    quantity_unit: str | None = Field(default=None, min_length=1, max_length=40)


class ProductCreate(BaseModel):
    """Pydantic model for a product post request body.

    :ivar name: The name of this warehouse.
    :type name: str
    """

    name: str = Field(min_length=2)


class ProductPatch(BaseModel):
    """Pydantic model for a product patch request body."""


class WarehouseCreate(BaseModel):
    """Pydantic model for a warehouse post request body.

    :ivar name: The name of this warehouse.
    :type name: str
    :ivar location: The location of this warehouse.
    :type location: str
    :ivar max_capacity: The capacity of this warehouse.
    :type max_capacity: int
    """

    name: str = Field(min_length=2)
    location: str = Field(min_length=2)
    max_capacity: int | None = Field(default=None, ge=1)


class WarehousePatch(BaseModel):
    """Pydantic model for a warehouse patch request body.

    :ivar location: The location of this warehouse.
    :type location: str
    :ivar max_capacity: The capacity of this warehouse.
    :type max_capacity: int
    """

    location: str | None = Field(default=None, min_length=2)
    max_capacity: int | None = Field(default=None, ge=1)


class DeliveryPosition(BaseModel):
    """Pydantic model for a delivery position request body."""

    material_id: uuid.UUID
    quantity: int


class Delivery(BaseModel):
    """Pydantic model for a delivery request body."""

    warehouse_id: uuid.UUID
    positions: list[DeliveryPosition]

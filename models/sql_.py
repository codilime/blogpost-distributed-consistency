"""SQLModel/Pydantic models for the Factory application."""

import typing as t
import uuid
from datetime import datetime

from pydantic import computed_field, model_validator
from slugify import slugify
from sqlalchemy import func, CheckConstraint
from sqlalchemy.types import DateTime
from sqlmodel import Field, Relationship, SQLModel


class DefaultMixin:
    """Mixin class providing a default unique identifier.

    This class auto-generates a unique UUID for the ``id`` attribute, which can
    be used as a primary key or other unique identifier in applications where
    such functionality is required.

    :ivar id: A unique identifier automatically generated using UUID.
    :type id: uuid.UUID
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class CreatedAtMixin:
    """Mixin class for adding a creation timestamp to inherited classes.

    This class is intended to be used as a base mixin to add a 'created_at'
    attribute, which represents the timestamp when the object was created.
    The timestamp automatically gets assigned the current datetime using a
    default SQLAlchemy function upon creation of the object.

    :ivar created_at: The timestamp denoting when the object was created.
    :type created_at: datetime
    """

    created_at: datetime = Field(sa_column_kwargs={"server_default": func.now()}, sa_type=DateTime)


class NamedMixin:
    name: str = Field(min_length=2, sa_column_kwargs={"unique": True})
    slug: str = Field(index=True, unique=True, min_length=1)

    __table_args__ = (
        CheckConstraint("length(name) > 1", name="name_at_least_2_characters"),
        CheckConstraint("length(slug) > 0", name="slug_not_empty"),
    )

    def __init__(self, **data) -> None:  # noqa: ANN002, ANN003, D107
        if "name" in data and "slug" not in data:
            data["slug"] = slugify(data["name"])
        super().__init__(**data)

    def __str__(self) -> str:
        return f"{camel_to_lower_with_spaces(self.__class__.__name__)} {self.name}"


class BOM(DefaultMixin, CreatedAtMixin, SQLModel, table=True):
    """A Bill of Materials (BOM) database representation.

    This class is used to associate a specific product with its materials and
    quantify the number of each material required. It is a database model
    designed to store BOM data with relations to `Product` and `Material`
    entities through foreign keys.

    :ivar id: A unique identifier automatically generated using UUID.
    :type id: uuid.UUID
    :ivar created_at: The timestamp denoting when the object was created.
    :type created_at: datetime
    :ivar product_id: The UUID of the product associated with this BOM.
    :type product_id: uuid.UUID
    :ivar material_id: The UUID of the material used in the BOM.
    :type material_id: uuid.UUID
    :ivar quantity: The number of the material required for the product.
    :type quantity: int
    """

    product_id: uuid.UUID = Field(default=None, foreign_key="product.id")
    material_id: uuid.UUID = Field(default=None, foreign_key="material.id")
    quantity: int = Field(default=1, sa_column_kwargs={"server_default": "1"})

    product: t.Union["Product", None] = Relationship(back_populates="boms")
    material: t.Union["Material", None] = Relationship(back_populates="boms")

    @computed_field
    def material_name(self) -> str | None:
        return self.material.name if self.material else None

    @computed_field
    def material_slug(self) -> str | None:
        return self.material.slug if self.material else None

    @computed_field
    def product_name(self) -> str | None:
        return self.product.name if self.product else None

    @computed_field
    def product_slug(self) -> str | None:
        return self.product.slug if self.product else None


class Product(DefaultMixin, CreatedAtMixin, NamedMixin, SQLModel, table=True):
    """Product entity database representation.

    This class serves as a model for a product, inheriting functionality
    from SQLModel for database integration as well as additional mixins
    for default ``id`` value and creation timestamp. It defines specific
    fields and attributes necessary for product storage and manipulation.

    :ivar id: A unique identifier automatically generated using UUID.
    :type id: uuid.UUID
    :ivar created_at: The timestamp denoting when the object was created.
    :type created_at: datetime
    :ivar name: The name of the product.
    :type name: str
    :ivar slug: The slug of the product. This field is indexed and must
        be unique to ensure that no two products have the same name.
    :type name: str
    """

    boms: list[BOM] | None = Relationship(back_populates="product")
    materials: list["Material"] | None = Relationship(
        back_populates="products",
        link_model=BOM,
        sa_relationship_kwargs={"viewonly": True},
    )


class StockPosition(DefaultMixin, CreatedAtMixin, SQLModel, table=True):
    """Stock of a specific material in a warehouse database representation.

    This class is a SQLModel table that keeps track of the quantity of a material
    located in a specific warehouse. It uses mixins to inherit common properties
    like unique ID and creation timestamp. The primary purpose of this class is to
    store and query stock levels for warehouse management systems.

    :ivar id: A unique identifier automatically generated using UUID.
    :type id: uuid.UUID
    :ivar created_at: The timestamp denoting when the object was created.
    :type created_at: datetime
    :ivar warehouse_id: The unique identifier of the warehouse where the
        material stock is stored.
    :type warehouse_id: uuid.UUID
    :ivar material_id: The unique identifier of the material whose stock
        is being tracked.
    :type material_id: uuid.UUID
    :ivar quantity: The amount of the material available in stock. Defaults
        to 0 if not specified.
    :type quantity: int
    """

    material_id: uuid.UUID = Field(default=None, foreign_key="material.id", ondelete="CASCADE")
    material: t.Union["Material", None] = Relationship(back_populates="stock")

    warehouse_id: uuid.UUID = Field(default=None, foreign_key="warehouse.id", ondelete="CASCADE")
    warehouse: t.Union["Warehouse", None] = Relationship(back_populates="stock")

    quantity: int = Field(default=0, sa_column_kwargs={"server_default": "0"})

    @computed_field
    def material_name(self) -> str | None:
        return self.material.name if self.material else None

    @computed_field
    def material_slug(self) -> str | None:
        return self.material.slug if self.material else None

    @computed_field
    def warehouse_name(self) -> str | None:
        return self.warehouse.name if self.warehouse else None

    @computed_field
    def warehouse_slug(self) -> str | None:
        return self.warehouse.slug if self.warehouse else None


class Material(DefaultMixin, CreatedAtMixin, NamedMixin, SQLModel, table=True):
    """A material entity database representation.

    This class is used to define the structure and behavior of a material,
    which includes information about its name, the unit of quantity, and any
    other potential attributes. It integrates with SQLModel for database
    operations as well as additional mixins for default ``id`` value and
    creation timestamp.

    :ivar id: A unique identifier automatically generated using UUID.
    :type id: uuid.UUID
    :ivar created_at: The timestamp denoting when the object was created.
    :type created_at: datetime
    :ivar name: The name of the material.
    :type name: str
    :ivar slug: The slug of the material. This field is indexed and must
        be unique to ensure that no two materials have the same name.
    :type name: str
    :ivar quantity_unit: Unit used to measure the quantity of the material.
    :type quantity_unit: str
    """

    quantity_unit: str

    boms: list[BOM] | None = Relationship(back_populates="material")
    stock: list["StockPosition"] | None = Relationship(
        back_populates="material",
        cascade_delete=True,
    )
    products: list["Product"] | None = Relationship(
        back_populates="materials",
        link_model=BOM,
        sa_relationship_kwargs={"viewonly": True},
    )
    warehouses: list["Warehouse"] | None = Relationship(
        back_populates="materials",
        link_model=StockPosition,
        sa_relationship_kwargs={"viewonly": True},
    )


class Warehouse(DefaultMixin, CreatedAtMixin, NamedMixin, SQLModel, table=True):
    """A warehouse entity database representation.

    The Warehouse class defines the structure and attributes of a warehouse
    entity for storage in a database table. It includes details such as the
    warehouse name and its location. The class inherits functionality from
    SQLModel, DefaultMixin, and CreatedAtMixin, providing database modeling
    capabilities, default behaviors, and created-at timestamp support.

    :ivar id: A unique identifier automatically generated using UUID.
    :type id: uuid.UUID
    :ivar created_at: The timestamp denoting when the object was created.
    :type created_at: datetime
    :ivar name: The name of the warehouse. It is unique and indexed in the
        database for efficient querying.
    :ivar name: The name of the warehouse.
    :type name: str
    :ivar slug: The slug of the warehouse. This field is indexed and must
        be unique to ensure that no two warehouses have the same name.
    :type name: str
    :ivar location: The geographical or physical location of the warehouse.
    :type location: str
    :ivar max_capacity: The number of items which can be stored in the warehouse.
    :type max_capacity: int
    """

    location: str = Field(min_length=2, sa_column_kwargs={"unique": True})
    max_capacity: int = Field(
        default=1000000, ge=1, sa_column_kwargs={"server_default": "1000000"}
    )

    stock: list[StockPosition] | None = Relationship(
        back_populates="warehouse",
        cascade_delete=True,
    )
    materials: list[Material] | None = Relationship(
        back_populates="warehouses",
        link_model=StockPosition,
        sa_relationship_kwargs={"viewonly": True},
    )

    @computed_field
    def capacity(self) -> int:
        if self.stock is None:
            return self.max_capacity
        return self.max_capacity - sum(s.quantity for s in self.stock)


def camel_to_lower_with_spaces(s):
    result = []
    for i, char in enumerate(s):
        if char.isupper() and i != 0:
            result.append(" ")
        result.append(char.lower())
    return "".join(result)

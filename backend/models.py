from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class OrderStatus(str, enum.Enum):
    """Order status enum"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    READY_FOR_PICKUP = "ready for pickup"
    PICKED_UP = "picked up"


class Order(Base):
    """Customer order from webshop"""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(50), nullable=True)
    customer_email = Column(String(255), nullable=True)
    batch_id = Column(String(100), nullable=False, index=True)
    batch_name = Column(String(255), nullable=False)
    pickup_info = Column(String(500), nullable=True)
    notes = Column(String(1000), nullable=True)
    total_amount = Column(Float, nullable=False)
    total_items = Column(Integer, nullable=False)
    status = Column(
        Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to order items
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order {self.id}: {self.customer_name} - {self.batch_name} - €{self.total_amount}>"


class OrderItem(Base):
    """Individual item in an order"""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

    def __repr__(self):
        return (
            f"<OrderItem {self.id}: {self.quantity}x "
            f"{self.product.name if self.product else 'product'}>"
        )

    @property
    def product_name(self) -> str:
        return self.product.name if self.product else ""

    @property
    def product_slug(self) -> str:
        return self.product.slug if self.product else ""

    @property
    def unit_price(self) -> float:
        return float(self.product.price) if self.product else 0.0

    @property
    def subtotal(self) -> float:
        return self.computed_subtotal

    @property
    def computed_subtotal(self) -> float:
        return self.unit_price * (self.quantity or 0)

    @property
    def packaging_info(self) -> str:
        if not self.product:
            return ""
        pieces = self.product.packaging_pieces
        grams = self.product.unit_grams
        if pieces and grams:
            return f"{pieces} stuks × ±{grams}g"
        if grams:
            return f"±{grams}g"
        if pieces:
            return f"{pieces} stuks"
        return ""


class Product(Base):
    """Sellable product definition."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    ingredients = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    weight_display = Column(String(100), nullable=False)
    packaging_pieces = Column(Integer, nullable=True)
    unit_grams = Column(Integer, nullable=True)
    image = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Product {self.slug}: {self.name} - €{self.price}>"


# Association table for many-to-many relationship between Batch and Product
batch_products = Table(
    "batch_products",
    Base.metadata,
    Column("batch_id", Integer, ForeignKey("batches.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
)


class Batch(Base):
    """Slaughter batch with pickup schedule"""

    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    pickup_location = Column(String(500), nullable=False)
    pickup_text = Column(String(255), nullable=True)  # For freezer: "Op afspraak"
    is_freezer = Column(Boolean, default=False, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    pickup_slots = relationship(
        "PickupSlot", back_populates="batch", cascade="all, delete-orphan"
    )
    products = relationship("Product", secondary=batch_products, backref="batches")

    def __repr__(self):
        return f"<Batch {self.slug}: {self.name}>"


class PickupSlot(Base):
    """Pickup time slot for a batch"""

    __tablename__ = "pickup_slots"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD format
    time = Column(String(50), nullable=False)  # e.g., "17:00 - 19:00"
    sort_order = Column(Integer, default=0, nullable=False)

    # Relationship
    batch = relationship("Batch", back_populates="pickup_slots")

    def __repr__(self):
        return f"<PickupSlot {self.date} {self.time}>"

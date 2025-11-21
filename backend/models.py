from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
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
    READY = "ready"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


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
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to order items
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order {self.id}: {self.customer_name} - {self.batch_name} - €{self.total_amount}>"


class OrderItem(Base):
    """Individual item in an order"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    expected_price = Column(Float, nullable=True)  # For per-kg items
    subtotal = Column(Float, nullable=False)
    packaging_info = Column(String(255), nullable=True)  # e.g., "2 stuks × ±250g"

    # Relationship to order
    order = relationship("Order", back_populates="items")

    def __repr__(self):
        return f"<OrderItem {self.id}: {self.quantity}x {self.product_name} - €{self.subtotal}>"


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
    packaging_grams = Column(Integer, nullable=True)
    image = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Product {self.slug}: {self.name} - €{self.price}>"

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
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

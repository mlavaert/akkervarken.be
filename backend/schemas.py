from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from models import OrderStatus


class OrderItemCreate(BaseModel):
    """Schema for creating an order item"""

    product_slug: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0, description="Quantity of items")


class OrderCreate(BaseModel):
    """Schema for creating a new order"""

    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=50)
    customer_email: Optional[EmailStr] = None
    batch_id: str = Field(..., min_length=1, max_length=100)
    batch_name: str = Field(..., min_length=1, max_length=255)
    pickup_info: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    items: List[OrderItemCreate] = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "customer_name": "Jan Janssens",
                "customer_phone": "+32494123456",
                "customer_email": "jan@example.com",
                "batch_id": "15-december-2024",
                "batch_name": "15 december 2024",
                "pickup_info": "2024-12-15 om 10:00, 2024-12-15 om 14:00",
                "notes": "Graag via achteringang leveren",
                "items": [
                    {
                        "product_slug": "gehakt",
                        "quantity": 2,
                    },
                    {
                        "product_slug": "spek",
                        "quantity": 1
                    },
                ],
            }
        }


class OrderItemResponse(BaseModel):
    """Schema for order item in responses"""

    id: int
    product_id: int
    product_slug: str
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float
    packaging_info: Optional[str]

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Schema for order in responses"""

    id: int
    customer_name: str
    customer_phone: Optional[str]
    customer_email: Optional[str]
    batch_id: str
    batch_name: str
    pickup_info: Optional[str]
    notes: Optional[str]
    total_amount: float
    total_items: int
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderCreateResponse(BaseModel):
    """Response after creating an order"""

    success: bool
    order_id: int
    message: str
    email_sent: bool = False


class ProductBase(BaseModel):
    """Shared fields for products"""

    slug: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    ingredients: Optional[str] = None
    price: float = Field(..., gt=0)
    weight_display: str = Field(..., min_length=1, max_length=100)
    packaging_pieces: Optional[int] = Field(None, ge=0)
    unit_grams: Optional[int] = Field(
        None, ge=0, description="Estimated weight per piece in grams"
    )
    image: Optional[str] = Field(None, max_length=255)


class ProductCreate(ProductBase):
    """Payload for creating a product"""

    pass


class ProductUpdate(BaseModel):
    """Payload for updating a product"""

    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    ingredients: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    weight_display: Optional[str] = Field(None, min_length=1, max_length=100)
    packaging_pieces: Optional[int] = Field(None, ge=0)
    unit_grams: Optional[int] = Field(
        None, ge=0, description="Estimated weight per piece in grams"
    )
    image: Optional[str] = Field(None, max_length=255)


class ProductResponse(ProductBase):
    """Response schema for a product"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

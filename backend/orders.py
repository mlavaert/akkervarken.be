from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Order, OrderItem, OrderStatus
from schemas import OrderCreate, OrderResponse, OrderCreateResponse
from email_service import email_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/", response_model=OrderCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order from the webshop.

    This endpoint:
    1. Validates the order data
    2. Saves the order to the database
    3. Sends confirmation email to customer (if email provided)
    4. Sends notification email to admin
    5. Returns the order ID and confirmation
    """
    try:
        # Create order record
        order = Order(
            customer_name=order_data.customer_name,
            customer_phone=order_data.customer_phone,
            customer_email=order_data.customer_email,
            batch_id=order_data.batch_id,
            batch_name=order_data.batch_name,
            pickup_info=order_data.pickup_info,
            notes=order_data.notes,
            total_amount=order_data.total_amount,
            total_items=order_data.total_items,
            status=OrderStatus.PENDING,
        )

        # Add order to session
        db.add(order)
        db.flush()  # Flush to get the order ID

        # Create order items
        for item_data in order_data.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                product_name=item_data.product_name,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                expected_price=item_data.expected_price,
                subtotal=item_data.subtotal,
                packaging_info=item_data.packaging_info,
            )
            db.add(order_item)

        # Commit the transaction
        db.commit()
        db.refresh(order)

        logger.info(f"Order #{order.id} created successfully for {order.customer_name}")

        # Prepare items for email
        email_items = [
            {
                "name": item.product_name,
                "quantity": item.quantity,
                "subtotal": item.subtotal,
            }
            for item in order.items
        ]

        # Send emails asynchronously
        email_sent = False

        # Send confirmation to customer if email provided
        if order.customer_email:
            try:
                customer_email_sent = await email_service.send_order_confirmation_to_customer(
                    customer_email=order.customer_email,
                    customer_name=order.customer_name,
                    order_id=order.id,
                    batch_name=order.batch_name,
                    pickup_info=order.pickup_info or "Wordt later bevestigd",
                    items=email_items,
                    total=order.total_amount,
                )
                email_sent = customer_email_sent
                logger.info(f"Customer confirmation email sent for order #{order.id}")
            except Exception as e:
                logger.error(f"Failed to send customer email for order #{order.id}: {str(e)}")

        # Send notification to admin
        try:
            await email_service.send_order_notification_to_admin(
                order_id=order.id,
                customer_name=order.customer_name,
                customer_phone=order.customer_phone or "Niet opgegeven",
                customer_email=order.customer_email or "Niet opgegeven",
                batch_name=order.batch_name,
                pickup_info=order.pickup_info or "Wordt later bevestigd",
                items=email_items,
                total=order.total_amount,
                notes=order.notes,
            )
            logger.info(f"Admin notification email sent for order #{order.id}")
        except Exception as e:
            logger.error(f"Failed to send admin email for order #{order.id}: {str(e)}")

        return OrderCreateResponse(
            success=True,
            order_id=order.id,
            message=f"Bestelling #{order.id} succesvol aangemaakt",
            email_sent=email_sent,
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create order: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fout bij het aanmaken van de bestelling: {str(e)}",
        )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Get a specific order by ID.

    Returns the full order details including all items.
    """
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bestelling #{order_id} niet gevonden",
        )

    return order


@router.get("/", response_model=list[OrderResponse])
def list_orders(
    skip: int = 0,
    limit: int = 100,
    batch_id: str = None,
    status_filter: OrderStatus = None,
    db: Session = Depends(get_db),
):
    """
    List all orders with optional filtering.

    Parameters:
    - skip: Number of orders to skip (for pagination)
    - limit: Maximum number of orders to return
    - batch_id: Filter by batch ID
    - status_filter: Filter by order status
    """
    query = db.query(Order)

    if batch_id:
        query = query.filter(Order.batch_id == batch_id)

    if status_filter:
        query = query.filter(Order.status == status_filter)

    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    return orders

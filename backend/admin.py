import os
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import Order, OrderStatus

templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

router = APIRouter(prefix="/admin", tags=["admin"])


def _get_admin_credentials() -> tuple[str, str]:
    """Load expected admin credentials from environment."""
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin access not configured",
        )
    return username, password


def require_admin(
    credentials: HTTPBasicCredentials = Depends(security),
) -> str:
    """Very small HTTP Basic auth guard for admin pages."""
    expected_username, expected_password = _get_admin_credentials()

    username_matches = secrets.compare_digest(credentials.username, expected_username)
    password_matches = secrets.compare_digest(credentials.password, expected_password)

    if not (username_matches and password_matches):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


@router.get("/orders", response_class=HTMLResponse)
def list_orders(
    request: Request,
    status_filter: Optional[OrderStatus] = None,
    limit: int = 200,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Render a minimal admin dashboard with recent orders."""
    query = db.query(Order).order_by(Order.created_at.desc())

    if status_filter:
        query = query.filter(Order.status == status_filter)

    orders = query.limit(limit).all()

    return templates.TemplateResponse(
        "admin/orders.html",
        {
            "request": request,
            "orders": orders,
            "status_filter": status_filter,
            "statuses": list(OrderStatus),
        },
    )


@router.post("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    new_status: OrderStatus = Form(...),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Update the status of a single order."""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order #{order_id} not found",
        )

    order.status = new_status
    db.add(order)
    db.commit()

    return RedirectResponse(url="/admin/orders?updated=1", status_code=status.HTTP_303_SEE_OTHER)

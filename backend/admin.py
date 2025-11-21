import os
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import Order, OrderStatus, Product

templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

router = APIRouter(prefix="/admin", tags=["admin"])


def _get_admin_credentials() -> tuple[str, str]:
    """Load expected admin credentials from environment."""
    username = os.getenv("ADMIN_EMAIL")
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


def _parse_price(value: str) -> float:
    """Parse a price value from a form field."""
    try:
        return float(value.replace(",", "."))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prijs moet een numerieke waarde zijn",
        )


def _parse_optional_int(value: Optional[str]) -> Optional[int]:
    """Convert optional numeric form fields to integers."""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aantal stuks/grammen moet numeriek zijn",
        )


@router.get("/orders", response_class=HTMLResponse)
def list_orders(
    request: Request,
    status_filter: Optional[str] = None,
    limit: int = 200,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Render a minimal admin dashboard with recent orders."""
    query = db.query(Order).order_by(Order.created_at.desc())

    status_filter_value: Optional[OrderStatus] = None
    if status_filter:
        try:
            status_filter_value = OrderStatus(status_filter)
            query = query.filter(Order.status == status_filter_value)
        except ValueError:
            status_filter_value = None  # ignore invalid filter input

    orders = query.limit(limit).all()

    return templates.TemplateResponse(
        "admin/orders.html",
        {
            "request": request,
            "orders": orders,
            "status_filter": status_filter_value,
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

    return RedirectResponse(
        url="/admin/orders?updated=1", status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/products", response_class=HTMLResponse)
def list_products(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Render the product management page."""
    products = db.query(Product).order_by(Product.name.asc()).all()
    return templates.TemplateResponse(
        "admin/products.html",
        {
            "request": request,
            "products": products,
            "created": request.query_params.get("created"),
            "saved": request.query_params.get("saved"),
            "deleted": request.query_params.get("deleted"),
        },
    )


@router.post("/products")
def create_product(
    slug: str = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    ingredients: Optional[str] = Form(None),
    price: str = Form(...),
    weight_display: str = Form(...),
    packaging_pieces: Optional[str] = Form(None),
    packaging_grams: Optional[str] = Form(None),
    image: Optional[str] = Form(None),
    is_active: bool = Form(False),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Create a product from the admin form."""
    slug_value = slug.strip()

    if db.query(Product).filter(Product.slug == slug_value).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product met deze slug bestaat al",
        )

    product = Product(
        slug=slug_value,
        name=name.strip(),
        description=description.strip(),
        ingredients=(ingredients or "").strip() or None,
        price=_parse_price(price),
        weight_display=weight_display.strip(),
        packaging_pieces=_parse_optional_int(packaging_pieces),
        packaging_grams=_parse_optional_int(packaging_grams),
        image=(image or "").strip() or None,
        is_active=is_active,
    )

    db.add(product)
    db.commit()

    return RedirectResponse(
        url="/admin/products?created=1", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/products/{product_id}/update")
def update_product(
    product_id: int,
    slug: str = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    ingredients: Optional[str] = Form(None),
    price: str = Form(...),
    weight_display: str = Form(...),
    packaging_pieces: Optional[str] = Form(None),
    packaging_grams: Optional[str] = Form(None),
    image: Optional[str] = Form(None),
    is_active: bool = Form(False),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Update an existing product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product niet gevonden"
        )

    slug_value = slug.strip()
    if slug_value != product.slug:
        if db.query(Product).filter(Product.slug == slug_value).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product met deze slug bestaat al",
            )
        product.slug = slug_value

    product.name = name.strip()
    product.description = description.strip()
    product.ingredients = (ingredients or "").strip() or None
    product.price = _parse_price(price)
    product.weight_display = weight_display.strip()
    product.packaging_pieces = _parse_optional_int(packaging_pieces)
    product.packaging_grams = _parse_optional_int(packaging_grams)
    product.image = (image or "").strip() or None
    product.is_active = is_active

    db.add(product)
    db.commit()

    return RedirectResponse(
        url="/admin/products?saved=1", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/products/{product_id}/delete")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Delete a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product niet gevonden"
        )

    db.delete(product)
    db.commit()

    return RedirectResponse(
        url="/admin/products?deleted=1", status_code=status.HTTP_303_SEE_OTHER
    )

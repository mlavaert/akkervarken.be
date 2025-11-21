from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from admin import require_admin
from database import get_db
from models import Product
from schemas import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/", response_model=list[ProductResponse])
def list_products(
    include_inactive: bool = False, db: Session = Depends(get_db)
) -> list[Product]:
    """Return the product catalog. Hides inactive items by default."""
    query = db.query(Product)
    if not include_inactive:
        query = query.filter(Product.is_active.is_(True))
    return query.order_by(Product.name.asc()).all()


@router.get("/{slug}", response_model=ProductResponse)
def get_product(slug: str, db: Session = Depends(get_db)) -> Product:
    """Fetch a single product by slug."""
    product = db.query(Product).filter(Product.slug == slug).first()
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product niet gevonden"
        )
    return product


@router.post(
    "/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED
)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
) -> Product:
    """Create a new product (admin only)."""
    existing = db.query(Product).filter(Product.slug == product_in.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product met deze slug bestaat al",
        )

    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
) -> Product:
    """Update a product (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product niet gevonden"
        )

    update_data = product_in.model_dump(exclude_unset=True)

    if "slug" in update_data:
        slug = update_data["slug"]
        if (
            slug
            and slug != product.slug
            and db.query(Product).filter(Product.slug == slug).first()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product met deze slug bestaat al",
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
) -> Response:
    """Delete a product (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product niet gevonden"
        )

    db.delete(product)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

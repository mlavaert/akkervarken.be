"""Batch management routes for admin panel."""

from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import Batch, PickupSlot, Product
from admin import require_admin

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/admin/batches", tags=["admin", "batches"])


@router.get("", response_class=HTMLResponse)
def list_batches(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """List all batches."""
    batches = db.query(Batch).order_by(Batch.is_active.desc(), Batch.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin/batches.html",
        {
            "request": request,
            "batches": batches,
            "created": request.query_params.get("created"),
            "saved": request.query_params.get("saved"),
            "deleted": request.query_params.get("deleted"),
        },
    )


@router.get("/new", response_class=HTMLResponse)
def new_batch_form(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Show form to create a new batch."""
    products = db.query(Product).order_by(Product.name).all()
    return templates.TemplateResponse(
        "admin/batch_form.html",
        {"request": request, "mode": "new", "batch": None, "products": products},
    )


@router.post("", response_class=RedirectResponse)
async def create_batch(
    request: Request,
    slug: str = Form(...),
    name: str = Form(...),
    pickup_location: str = Form(...),
    pickup_text: Optional[str] = Form(None),
    is_freezer: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Create a new batch."""
    # Get form data manually for lists
    form_data = await request.form()
    product_ids = form_data.getlist("product_ids")
    slot_dates = form_data.getlist("slot_dates")
    slot_times = form_data.getlist("slot_times")

    # Create batch
    batch = Batch(
        slug=slug.strip(),
        name=name.strip(),
        pickup_location=pickup_location.strip(),
        pickup_text=pickup_text.strip() if pickup_text else None,
        is_freezer=(is_freezer == "true"),
        is_active=(is_active == "true"),
    )
    db.add(batch)
    db.flush()  # Get batch.id

    # Add products
    if product_ids:
        product_id_ints = [int(pid) for pid in product_ids]
        products = db.query(Product).filter(Product.id.in_(product_id_ints)).all()
        batch.products = products

    # Add pickup slots
    for i, (date, time) in enumerate(zip(slot_dates, slot_times)):
        if date and time:  # Only add if both date and time are provided
            slot = PickupSlot(
                batch_id=batch.id, date=date, time=time, sort_order=i
            )
            db.add(slot)

    db.commit()
    return RedirectResponse(
        url="/admin/batches?created=1", status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/{batch_id}/edit", response_class=HTMLResponse)
def edit_batch_form(
    batch_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Show form to edit a batch."""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Batch niet gevonden"
        )

    products = db.query(Product).order_by(Product.name).all()
    return templates.TemplateResponse(
        "admin/batch_form.html",
        {
            "request": request,
            "mode": "edit",
            "batch": batch,
            "products": products,
        },
    )


@router.post("/{batch_id}/update", response_class=RedirectResponse)
async def update_batch(
    batch_id: int,
    request: Request,
    slug: str = Form(...),
    name: str = Form(...),
    pickup_location: str = Form(...),
    pickup_text: Optional[str] = Form(None),
    is_freezer: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Update an existing batch."""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Batch niet gevonden"
        )

    # Get form data manually for lists
    form_data = await request.form()
    product_ids = form_data.getlist("product_ids")
    slot_dates = form_data.getlist("slot_dates")
    slot_times = form_data.getlist("slot_times")

    # Update batch fields
    batch.slug = slug.strip()
    batch.name = name.strip()
    batch.pickup_location = pickup_location.strip()
    batch.pickup_text = pickup_text.strip() if pickup_text else None
    batch.is_freezer = (is_freezer == "true")
    batch.is_active = (is_active == "true")

    # Update products
    if product_ids:
        product_id_ints = [int(pid) for pid in product_ids]
        products = db.query(Product).filter(Product.id.in_(product_id_ints)).all()
        batch.products = products
    else:
        batch.products = []

    # Delete existing pickup slots and recreate
    db.query(PickupSlot).filter(PickupSlot.batch_id == batch_id).delete()

    # Add new pickup slots
    for i, (date, time) in enumerate(zip(slot_dates, slot_times)):
        if date and time:
            slot = PickupSlot(
                batch_id=batch.id, date=date, time=time, sort_order=i
            )
            db.add(slot)

    db.commit()
    return RedirectResponse(
        url="/admin/batches?saved=1", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/{batch_id}/delete", response_class=RedirectResponse)
def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Delete a batch."""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Batch niet gevonden"
        )

    db.delete(batch)
    db.commit()
    return RedirectResponse(
        url="/admin/batches?deleted=1", status_code=status.HTTP_303_SEE_OTHER
    )

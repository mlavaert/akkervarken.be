"""Batch management routes for admin panel."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Batch, PickupSlot, Product

router = APIRouter(prefix="/admin/batches", tags=["admin", "batches"])


@router.get("", response_class=HTMLResponse)
def list_batches(request: Request, created: bool = False, saved: bool = False, deleted: bool = False):
    """List all batches."""
    db: Session = next(get_db())
    try:
        batches = db.query(Batch).order_by(Batch.is_active.desc(), Batch.created_at.desc()).all()
        return request.app.state.templates.TemplateResponse(
            "admin/batches.html",
            {
                "request": request,
                "batches": batches,
                "created": created,
                "saved": saved,
                "deleted": deleted,
            },
        )
    finally:
        db.close()


@router.get("/new", response_class=HTMLResponse)
def new_batch_form(request: Request):
    """Show form to create a new batch."""
    db: Session = next(get_db())
    try:
        products = db.query(Product).order_by(Product.name).all()
        return request.app.state.templates.TemplateResponse(
            "admin/batch_form.html",
            {"request": request, "mode": "new", "batch": None, "products": products},
        )
    finally:
        db.close()


@router.post("", response_class=RedirectResponse)
def create_batch(
    request: Request,
    slug: str = Form(...),
    name: str = Form(...),
    pickup_location: str = Form(...),
    pickup_text: str = Form(None),
    is_freezer: bool = Form(False),
    is_active: bool = Form(True),
    product_ids: list[int] = Form([]),
    slot_dates: list[str] = Form([]),
    slot_times: list[str] = Form([]),
):
    """Create a new batch."""
    db: Session = next(get_db())
    try:
        # Create batch
        batch = Batch(
            slug=slug,
            name=name,
            pickup_location=pickup_location,
            pickup_text=pickup_text if pickup_text else None,
            is_freezer=is_freezer,
            is_active=is_active,
        )
        db.add(batch)
        db.flush()  # Get batch.id

        # Add products
        if product_ids:
            products = db.query(Product).filter(Product.id.in_(product_ids)).all()
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
            url="/admin/batches?created=true", status_code=303
        )
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@router.get("/{batch_id}/edit", response_class=HTMLResponse)
def edit_batch_form(request: Request, batch_id: int):
    """Show form to edit a batch."""
    db: Session = next(get_db())
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            return RedirectResponse(url="/admin/batches", status_code=303)

        products = db.query(Product).order_by(Product.name).all()
        return request.app.state.templates.TemplateResponse(
            "admin/batch_form.html",
            {
                "request": request,
                "mode": "edit",
                "batch": batch,
                "products": products,
            },
        )
    finally:
        db.close()


@router.post("/{batch_id}/update", response_class=RedirectResponse)
def update_batch(
    request: Request,
    batch_id: int,
    slug: str = Form(...),
    name: str = Form(...),
    pickup_location: str = Form(...),
    pickup_text: str = Form(None),
    is_freezer: bool = Form(False),
    is_active: bool = Form(True),
    product_ids: list[int] = Form([]),
    slot_dates: list[str] = Form([]),
    slot_times: list[str] = Form([]),
):
    """Update an existing batch."""
    db: Session = next(get_db())
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            return RedirectResponse(url="/admin/batches", status_code=303)

        # Update batch fields
        batch.slug = slug
        batch.name = name
        batch.pickup_location = pickup_location
        batch.pickup_text = pickup_text if pickup_text else None
        batch.is_freezer = is_freezer
        batch.is_active = is_active

        # Update products
        products = db.query(Product).filter(Product.id.in_(product_ids)).all() if product_ids else []
        batch.products = products

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
            url="/admin/batches?saved=true", status_code=303
        )
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@router.post("/{batch_id}/delete", response_class=RedirectResponse)
def delete_batch(request: Request, batch_id: int):
    """Delete a batch."""
    db: Session = next(get_db())
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if batch:
            db.delete(batch)
            db.commit()
        return RedirectResponse(
            url="/admin/batches?deleted=true", status_code=303
        )
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

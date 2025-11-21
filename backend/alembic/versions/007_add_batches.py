"""Add batches and pickup slots tables

Revision ID: 007
Revises: 006
Create Date: 2025-11-21

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create batches table
    op.create_table(
        "batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("pickup_location", sa.String(length=500), nullable=False),
        sa.Column("pickup_text", sa.String(length=255), nullable=True),
        sa.Column("is_freezer", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_batches_id", "batches", ["id"])
    op.create_index("ix_batches_slug", "batches", ["slug"], unique=True)
    op.create_index("ix_batches_is_freezer", "batches", ["is_freezer"])
    op.create_index("ix_batches_is_active", "batches", ["is_active"])

    # Create pickup_slots table
    op.create_table(
        "pickup_slots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.String(length=10), nullable=False),
        sa.Column("time", sa.String(length=50), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["batch_id"], ["batches.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pickup_slots_id", "pickup_slots", ["id"])
    op.create_index("ix_pickup_slots_batch_id", "pickup_slots", ["batch_id"])

    # Create batch_products association table
    op.create_table(
        "batch_products",
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["batches.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("batch_id", "product_id"),
    )


def downgrade() -> None:
    op.drop_table("batch_products")
    op.drop_index("ix_pickup_slots_batch_id", table_name="pickup_slots")
    op.drop_index("ix_pickup_slots_id", table_name="pickup_slots")
    op.drop_table("pickup_slots")
    op.drop_index("ix_batches_is_active", table_name="batches")
    op.drop_index("ix_batches_is_freezer", table_name="batches")
    op.drop_index("ix_batches_slug", table_name="batches")
    op.drop_index("ix_batches_id", table_name="batches")
    op.drop_table("batches")

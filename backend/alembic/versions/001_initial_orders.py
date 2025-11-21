"""Initial orders tables

Revision ID: 001
Revises:
Create Date: 2024-11-21

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create orders table
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=False),
        sa.Column("customer_phone", sa.String(length=50), nullable=True),
        sa.Column("customer_email", sa.String(length=255), nullable=True),
        sa.Column("batch_id", sa.String(length=100), nullable=False),
        sa.Column("batch_name", sa.String(length=255), nullable=False),
        sa.Column("pickup_info", sa.String(length=500), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("total_items", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "CONFIRMED",
                "READY",
                "FULFILLED",
                "CANCELLED",
                name="orderstatus",
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_id", "orders", ["id"])
    op.create_index("ix_orders_batch_id", "orders", ["batch_id"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_created_at", "orders", ["created_at"])

    # Create order_items table
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.String(length=100), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.Column("expected_price", sa.Float(), nullable=True),
        sa.Column("subtotal", sa.Float(), nullable=False),
        sa.Column("packaging_info", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_order_items_id", "order_items", ["id"])
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])


def downgrade() -> None:
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_index("ix_order_items_id", table_name="order_items")
    op.drop_table("order_items")

    op.drop_index("ix_orders_created_at", table_name="orders")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_batch_id", table_name="orders")
    op.drop_index("ix_orders_id", table_name="orders")
    op.drop_table("orders")

    # Drop enum type
    sa.Enum(name="orderstatus").drop(op.get_bind(), checkfirst=True)

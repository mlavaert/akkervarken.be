"""Link order items to products and drop redundant fields

Revision ID: 005
Revises: 004
Create Date: 2024-11-22

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add temporary new column for product FK
    op.add_column(
        "order_items",
        sa.Column("product_ref_id", sa.Integer(), nullable=True),
    )
    op.create_index("ix_order_items_product_ref_id", "order_items", ["product_ref_id"])
    op.create_foreign_key(
        "fk_order_items_product_ref_id_products",
        source_table="order_items",
        referent_table="products",
        local_cols=["product_ref_id"],
        remote_cols=["id"],
    )

    # Backfill using slug stored in old product_id column
    op.execute(
        """
        UPDATE order_items oi
        SET product_ref_id = p.id
        FROM products p
        WHERE oi.product_id::text = p.slug
        """
    )

    # Set not null after backfill
    op.alter_column("order_items", "product_ref_id", nullable=False)

    # Drop obsolete columns
    op.drop_column("order_items", "product_name")
    op.drop_column("order_items", "unit_price")
    op.drop_column("order_items", "expected_price")
    op.drop_column("order_items", "subtotal")
    op.drop_column("order_items", "packaging_info")

    # Drop old slug column
    op.drop_column("order_items", "product_id", mssql_drop_default=True)

    # Rename ref column to product_id
    op.alter_column("order_items", "product_ref_id", new_column_name="product_id")
    op.create_index("ix_order_items_product_id", "order_items", ["product_id"])
    op.drop_index("ix_order_items_product_ref_id", table_name="order_items")
    op.drop_constraint("fk_order_items_product_ref_id_products", "order_items", type_="foreignkey")
    op.create_foreign_key(
        "fk_order_items_product_id_products",
        source_table="order_items",
        referent_table="products",
        local_cols=["product_id"],
        remote_cols=["id"],
    )


def downgrade() -> None:
    # Drop FK and rename column back to product_ref_id for transition
    op.drop_constraint("fk_order_items_product_id_products", "order_items", type_="foreignkey")
    op.drop_index("ix_order_items_product_id", table_name="order_items")
    op.alter_column("order_items", "product_id", new_column_name="product_ref_id")
    op.create_index("ix_order_items_product_ref_id", "order_items", ["product_ref_id"])
    op.create_foreign_key(
        "fk_order_items_product_ref_id_products",
        source_table="order_items",
        referent_table="products",
        local_cols=["product_ref_id"],
        remote_cols=["id"],
    )

    # Recreate old slug column and redundant fields
    op.add_column(
        "order_items",
        sa.Column("product_id", sa.String(length=100), nullable=False, server_default=""),
    )
    op.add_column(
        "order_items",
        sa.Column("product_name", sa.String(length=255), nullable=False, server_default=""),
    )
    op.add_column(
        "order_items",
        sa.Column("unit_price", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "order_items",
        sa.Column("expected_price", sa.Float(), nullable=True),
    )
    op.add_column(
        "order_items",
        sa.Column("subtotal", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "order_items",
        sa.Column("packaging_info", sa.String(length=255), nullable=True),
    )

    # Backfill slug from products
    op.execute(
        """
        UPDATE order_items oi
        SET product_id = p.slug
        FROM products p
        WHERE oi.product_ref_id = p.id
        """
    )

    # Drop temp fk/index and column
    op.drop_constraint("fk_order_items_product_ref_id_products", "order_items", type_="foreignkey")
    op.drop_index("ix_order_items_product_ref_id", table_name="order_items")
    op.drop_column("order_items", "product_ref_id", mssql_drop_default=True)

"""Remove product is_active flag

Revision ID: 003
Revises: 002
Create Date: 2024-11-22

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_products_is_active", table_name="products")
    op.drop_column("products", "is_active")


def downgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )
    op.create_index("ix_products_is_active", "products", ["is_active"])

"""Remove redundant order fields (batch_name, pickup_info, total_amount, total_items)

Revision ID: 008
Revises: 007
Create Date: 2025-11-21

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove redundant columns that can be calculated from relationships
    op.drop_column("orders", "batch_name")
    op.drop_column("orders", "pickup_info")
    op.drop_column("orders", "total_amount")
    op.drop_column("orders", "total_items")


def downgrade() -> None:
    # Restore columns with default values
    # Note: Data will need to be recalculated after downgrade
    op.add_column(
        "orders",
        sa.Column("batch_name", sa.String(length=255), nullable=False, server_default=""),
    )
    op.add_column(
        "orders",
        sa.Column("pickup_info", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("total_amount", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "orders",
        sa.Column("total_items", sa.Integer(), nullable=False, server_default="0"),
    )

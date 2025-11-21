"""Use unit weight per piece instead of package weight

Revision ID: 004
Revises: 003
Create Date: 2024-11-22

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new column for per-piece weight
    op.add_column(
        "products",
        sa.Column("unit_grams", sa.Integer(), nullable=True),
    )

    # Copy data from packaging_grams to unit_grams, dividing by pieces if available
    op.execute(
        """
        UPDATE products
        SET unit_grams = CASE
            WHEN packaging_pieces IS NOT NULL AND packaging_pieces > 0 AND packaging_grams IS NOT NULL
            THEN CEILING(packaging_grams::numeric / packaging_pieces)::int
            ELSE packaging_grams
        END
        """
    )

    # Drop old column
    op.drop_column("products", "packaging_grams")


def downgrade() -> None:
    # Reintroduce packaging_grams
    op.add_column(
        "products",
        sa.Column("packaging_grams", sa.Integer(), nullable=True),
    )

    # Copy unit weight back into package weight (multiply by pieces if present)
    op.execute(
        """
        UPDATE products
        SET packaging_grams = CASE
            WHEN packaging_pieces IS NOT NULL AND packaging_pieces > 0 AND unit_grams IS NOT NULL
            THEN packaging_pieces * unit_grams
            ELSE unit_grams
        END
        """
    )

    op.drop_column("products", "unit_grams")

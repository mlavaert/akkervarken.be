"""Simplify order statuses to pending, confirmed, ready for pickup, picked up

Revision ID: 006
Revises: 005
Create Date: 2025-11-21

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL requires a multi-step approach to change enum values

    # Step 1: Create new enum type with simplified statuses
    op.execute("CREATE TYPE orderstatus_new AS ENUM ('pending', 'confirmed', 'ready for pickup', 'picked up')")

    # Step 2: Migrate existing data to new statuses
    # Map old statuses to new ones:
    # - pending -> pending
    # - confirmed -> confirmed
    # - ready -> ready for pickup
    # - fulfilled -> picked up
    # - cancelled -> pending (rare case, keep as pending)
    op.execute("""
        ALTER TABLE orders
        ALTER COLUMN status TYPE orderstatus_new
        USING (
            CASE status::text
                WHEN 'pending' THEN 'pending'::orderstatus_new
                WHEN 'confirmed' THEN 'confirmed'::orderstatus_new
                WHEN 'ready' THEN 'ready for pickup'::orderstatus_new
                WHEN 'fulfilled' THEN 'picked up'::orderstatus_new
                WHEN 'cancelled' THEN 'pending'::orderstatus_new
                ELSE 'pending'::orderstatus_new
            END
        )
    """)

    # Step 3: Drop old enum type
    op.execute("DROP TYPE orderstatus")

    # Step 4: Rename new type to original name
    op.execute("ALTER TYPE orderstatus_new RENAME TO orderstatus")


def downgrade() -> None:
    # Restore original enum with all statuses
    op.execute("CREATE TYPE orderstatus_new AS ENUM ('pending', 'confirmed', 'ready', 'fulfilled', 'cancelled')")

    # Map new statuses back to old ones (best effort)
    op.execute("""
        ALTER TABLE orders
        ALTER COLUMN status TYPE orderstatus_new
        USING (
            CASE status::text
                WHEN 'pending' THEN 'pending'::orderstatus_new
                WHEN 'confirmed' THEN 'confirmed'::orderstatus_new
                WHEN 'ready for pickup' THEN 'ready'::orderstatus_new
                WHEN 'picked up' THEN 'fulfilled'::orderstatus_new
                ELSE 'pending'::orderstatus_new
            END
        )
    """)

    op.execute("DROP TYPE orderstatus")
    op.execute("ALTER TYPE orderstatus_new RENAME TO orderstatus")

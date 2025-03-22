"""route segments

Revision ID: route_segments
Revises: improve_route_structure
Create Date: 2024-03-21 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "route_segments"
down_revision = "improve_route_structure"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create route_segments table
    op.create_table(
        "route_segments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("start_point", sa.JSON(), nullable=False),
        sa.Column("end_point", sa.JSON(), nullable=False),
        sa.Column("geometry", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["route_id"],
            ["routes.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Add indexes for better query performance
    op.create_index("ix_route_segments_route_id", "route_segments", ["route_id"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_route_segments_route_id")

    # Drop table
    op.drop_table("route_segments")

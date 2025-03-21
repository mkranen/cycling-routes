"""min and max coordinates added

Revision ID: 2b2a335dab60
Revises: 79f053683ec4
Create Date: 2025-01-02 19:34:57.480364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '2b2a335dab60'
down_revision: Union[str, None] = '79f053683ec4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('routes', sa.Column('min_lat', sa.Float(), nullable=True))
    op.add_column('routes', sa.Column('min_lng', sa.Float(), nullable=True))
    op.add_column('routes', sa.Column('max_lat', sa.Float(), nullable=True))
    op.add_column('routes', sa.Column('max_lng', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('routes', 'max_lng')
    op.drop_column('routes', 'max_lat')
    op.drop_column('routes', 'min_lng')
    op.drop_column('routes', 'min_lat')
    # ### end Alembic commands ###

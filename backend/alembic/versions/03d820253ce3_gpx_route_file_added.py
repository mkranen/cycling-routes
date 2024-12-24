"""gpx route file added

Revision ID: 03d820253ce3
Revises: 5ad29b92649d
Create Date: 2024-12-24 17:56:22.693676

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03d820253ce3'
down_revision: Union[str, None] = '5ad29b92649d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('routes', sa.Column('gpx_file_path', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('routes', 'gpx_file_path')
    # ### end Alembic commands ###

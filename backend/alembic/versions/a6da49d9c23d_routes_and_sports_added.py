"""routes and sports added

Revision ID: a6da49d9c23d
Revises: a8393ff27d9f
Create Date: 2025-01-01 16:33:39.684970

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a6da49d9c23d'
down_revision: Union[str, None] = 'a8393ff27d9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('routes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('sport_id', sa.Integer(), nullable=True),
    sa.Column('komoot_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['komoot_id'], ['komoot_routes.id'], ),
    sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('routes')
    op.drop_table('sports')
    # ### end Alembic commands ###

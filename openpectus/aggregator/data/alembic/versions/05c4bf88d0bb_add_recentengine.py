"""Add RecentEngine

Revision ID: 05c4bf88d0bb
Revises: d517729a9be0
Create Date: 2024-06-24 13:53:40.744147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05c4bf88d0bb'
down_revision: Union[str, None] = 'd517729a9be0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('RecentEngines',
    sa.Column('engine_id', sa.String(), nullable=False),
    sa.Column('run_id', sa.String(), nullable=True),
    sa.Column('run_started', sa.DateTime(), nullable=True),
    sa.Column('run_stopped', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('system_state', sa.String(), nullable=False),
    sa.Column('location', sa.String(), nullable=False),
    sa.Column('last_update', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_RecentEngines')),
    sa.UniqueConstraint('engine_id', name=op.f('uq_RecentEngines_engine_id'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('RecentEngines')
    # ### end Alembic commands ###
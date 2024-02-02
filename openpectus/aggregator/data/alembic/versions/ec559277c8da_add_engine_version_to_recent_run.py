"""add engine_version to recent_run

Revision ID: ec559277c8da
Revises: 72449425de7c
Create Date: 2024-02-02 11:55:49.427312

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from openpectus import __version__

# revision identifiers, used by Alembic.
revision: str = 'ec559277c8da'
down_revision: Union[str, None] = '72449425de7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('RecentRuns', schema=None) as batch_op:
        batch_op.add_column(sa.Column('engine_version', sa.String(), nullable=False, server_default=__version__))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('RecentRuns', schema=None) as batch_op:
        batch_op.drop_column('engine_version')

    # ### end Alembic commands ###

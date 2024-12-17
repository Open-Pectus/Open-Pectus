"""sad contributors to recent engine

Revision ID: cfb648a71b50
Revises: bcda1e0dd461
Create Date: 2024-12-16 13:58:44.694728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cfb648a71b50'
down_revision: Union[str, None] = 'bcda1e0dd461'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('RecentEngines', schema=None) as batch_op:
        batch_op.add_column(sa.Column('contributors', sa.JSON(), nullable=False, server_default='[]'))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('RecentEngines', schema=None) as batch_op:
        batch_op.drop_column('contributors')

    # ### end Alembic commands ###

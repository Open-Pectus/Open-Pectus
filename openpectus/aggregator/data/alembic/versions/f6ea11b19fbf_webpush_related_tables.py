"""WebPush related tables

Revision ID: f6ea11b19fbf
Revises: cfb648a71b50
Create Date: 2025-06-16 15:41:40.382937

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6ea11b19fbf'
down_revision: Union[str, None] = 'cfb648a71b50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('WebPushNotificationPreferences',
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('user_roles', sa.JSON(), nullable=False),
    sa.Column('scope', sa.Enum('PROCESS_UNITS_WITH_RUNS_IVE_CONTRIBUTED_TO', 'PROCESS_UNITS_I_HAVE_ACCESS_TO', 'SPECIFIC_PROCESS_UNITS', name='notificationscope'), nullable=False),
    sa.Column('topics', sa.JSON(), nullable=False),
    sa.Column('process_units', sa.JSON(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_WebPushNotificationPreferences')),
    sa.UniqueConstraint('user_id', name=op.f('uq_WebPushNotificationPreferences_user_id'))
    )
    op.create_table('WebPushSubscriptions',
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('endpoint', sa.String(), nullable=False),
    sa.Column('auth', sa.String(), nullable=False),
    sa.Column('p256dh', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_WebPushSubscriptions'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('WebPushSubscriptions')
    op.drop_table('WebPushNotificationPreferences')
    # ### end Alembic commands ###

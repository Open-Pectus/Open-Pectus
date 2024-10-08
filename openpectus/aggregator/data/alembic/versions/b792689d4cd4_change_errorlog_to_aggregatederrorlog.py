"""Change ErrorLog to AggregatedErrorLog

Revision ID: b792689d4cd4
Revises: 774e4df9ce40
Create Date: 2024-10-08 09:43:26.241195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b792689d4cd4'
down_revision: Union[str, None] = '774e4df9ce40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The only difference between ErrorLog and AggregatedErrorLog is the addition of the field
    # occurrences which has a default value of 1. It appears to work without changes.
    pass


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

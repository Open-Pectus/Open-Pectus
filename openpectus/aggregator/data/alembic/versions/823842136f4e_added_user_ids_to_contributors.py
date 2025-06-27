"""Added user ids to contributors

Revision ID: 823842136f4e
Revises: f6ea11b19fbf
Create Date: 2025-06-18 09:45:51.679869

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '823842136f4e'
down_revision: Union[str, None] = 'f6ea11b19fbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE RecentEngines SET contributors = '[]'")
    op.execute("UPDATE RecentRuns SET contributors = '[]'")

def downgrade() -> None:
    pass

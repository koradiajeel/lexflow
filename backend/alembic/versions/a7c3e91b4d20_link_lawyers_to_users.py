"""link lawyers to users (lawyers.user_id)

Revision ID: a7c3e91b4d20
Revises: 2e813b73e948
Create Date: 2026-10-12 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7c3e91b4d20'
down_revision: Union[str, Sequence[str], None] = '2e813b73e948'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Optional link from a lawyer profile to their login account.
    op.add_column('lawyers', sa.Column('user_id', sa.Uuid(), nullable=True))
    op.create_unique_constraint('uq_lawyers_user_id', 'lawyers', ['user_id'])
    op.create_foreign_key(
        'fk_lawyers_user_id_users', 'lawyers', 'users',
        ['user_id'], ['id'], ondelete='SET NULL',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_lawyers_user_id_users', 'lawyers', type_='foreignkey')
    op.drop_constraint('uq_lawyers_user_id', 'lawyers', type_='unique')
    op.drop_column('lawyers', 'user_id')

"""add_default_status_to_trip_invites

Revision ID: bcbfa4f95cf8
Revises: 7285c6cf6b8f
Create Date: 2025-12-05 13:57:18.635521

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcbfa4f95cf8'
down_revision: Union[str, Sequence[str], None] = '7285c6cf6b8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add server default to status column
    op.alter_column('trip_invites', 'status',
                    server_default='pending',
                    existing_type=sa.String(length=20),
                    existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove server default from status column
    op.alter_column('trip_invites', 'status',
                    server_default=None,
                    existing_type=sa.String(length=20),
                    existing_nullable=False)

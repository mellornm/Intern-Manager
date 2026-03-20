"""add phone column to interns

Revision ID: 848e5673bec7
Revises: 99ba672f4663
Create Date: 2026-03-20 18:10:13.598496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '848e5673bec7'
down_revision: Union[str, Sequence[str], None] = '99ba672f4663'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add phone to interns (nullable)
    with op.batch_alter_table('interns', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone', sa.String(), nullable=True))
    
    # Add meeting_topic to meetings (with default)
    with op.batch_alter_table('meetings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('meeting_topic', sa.String(), 
                                      server_default='General Follow-up', 
                                      nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('meetings', schema=None) as batch_op:
        batch_op.drop_column('meeting_topic')
    
    with op.batch_alter_table('interns', schema=None) as batch_op:
        batch_op.drop_column('phone')

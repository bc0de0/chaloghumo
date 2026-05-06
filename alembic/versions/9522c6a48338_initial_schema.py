"""Initial schema

Revision ID: 9522c6a48338
Revises: 
Create Date: 2026-05-06 11:28:09.187598

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9522c6a48338'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create RegionType Enum
    op.execute("CREATE TYPE regiontype AS ENUM ('Coastal', 'Alpine', 'Urban', 'Rural', 'Desert')")
    
    # Create destinations table
    op.create_table(
        'destinations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lng', sa.Float(), nullable=False),
        sa.Column('elevation', sa.Float(), nullable=True),
        sa.Column('region_type', sa.Enum('COASTAL', 'ALPINE', 'URBAN', 'RURAL', 'DESERT', name='regiontype'), nullable=False),
        sa.Column('base_vibe', sa.JSON(), nullable=False),
        sa.Column('dynamic_state', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_destinations_name'), 'destinations', ['name'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('preferences', sa.JSON(), nullable=False),
        sa.Column('constraints', sa.JSON(), nullable=False),
        sa.Column('mood', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

def downgrade() -> None:
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_destinations_name'), table_name='destinations')
    op.drop_table('destinations')
    op.execute("DROP TYPE regiontype")

"""role updated

Revision ID: d236fbbe209d
Revises: 717f34a8a6be
Create Date: 2026-05-30 07:44:02.308845

"""
from alembic import op
import sqlalchemy as sa


revision = 'd236fbbe209d'
down_revision = '717f34a8a6be'
branch_labels = None
depends_on = None


def upgrade():
    user_roles = sa.Enum(
        'user',
        'staff',
        'manager',
        'admin',
        name='user_roles'
    )

    user_roles.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        'user',
        'role',
        existing_type=sa.VARCHAR(length=20),
        type_=user_roles,
        existing_nullable=False,
        postgresql_using='role::user_roles'
    )


def downgrade():
    user_roles = sa.Enum(
        'user',
        'staff',
        'manager',
        'admin',
        name='user_roles'
    )

    op.alter_column(
        'user',
        'role',
        existing_type=user_roles,
        type_=sa.VARCHAR(length=20),
        existing_nullable=False,
        postgresql_using='role::varchar'
    )

    user_roles.drop(op.get_bind(), checkfirst=True)
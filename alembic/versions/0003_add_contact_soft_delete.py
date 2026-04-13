"""add contact soft delete fields

Revision ID: 0003_add_contact_soft_delete
Revises: 0002_add_user_created_by
Create Date: 2026-04-13
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_add_contact_soft_delete"
down_revision = "0002_add_user_created_by"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "contacts",
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("contacts", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("contacts", "deleted_at")
    op.drop_column("contacts", "is_deleted")

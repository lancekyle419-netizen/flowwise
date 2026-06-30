"""Usage logging table migration.

Revision ID: 002_add_usage_logs
Revises: 001_initial_schema
Create Date: 2026-06-30 12:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_add_usage_logs"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "usage_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_used_gb", sa.Numeric(10, 2), nullable=False),
        sa.Column("logged_date", sa.Date(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usage_logs_subscription_id", "usage_logs", ["subscription_id"])
    op.create_index("ix_usage_logs_logged_date", "usage_logs", ["logged_date"])


def downgrade() -> None:
    op.drop_index("ix_usage_logs_logged_date", table_name="usage_logs")
    op.drop_index("ix_usage_logs_subscription_id", table_name="usage_logs")
    op.drop_table("usage_logs")

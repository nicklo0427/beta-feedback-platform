"""Add task resolution baseline fields."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260412_000002"
down_revision = "20260410_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("resolution_outcome", sa.String(), nullable=True))
    op.add_column("tasks", sa.Column("resolution_note", sa.Text(), nullable=True))
    op.add_column("tasks", sa.Column("resolved_at", sa.String(), nullable=True))
    op.add_column("tasks", sa.Column("resolved_by_account_id", sa.String(), nullable=True))
    op.create_index(
        "ix_tasks_resolved_by_account_id",
        "tasks",
        ["resolved_by_account_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_tasks_resolved_by_account_id", table_name="tasks")
    op.drop_column("tasks", "resolved_by_account_id")
    op.drop_column("tasks", "resolved_at")
    op.drop_column("tasks", "resolution_note")
    op.drop_column("tasks", "resolution_outcome")

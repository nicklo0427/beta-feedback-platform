"""Add activity events baseline."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260412_000003"
down_revision = "20260412_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "activity_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("actor_account_id", sa.String(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_activity_events_entity_type",
        "activity_events",
        ["entity_type"],
        unique=False,
    )
    op.create_index(
        "ix_activity_events_entity_id",
        "activity_events",
        ["entity_id"],
        unique=False,
    )
    op.create_index(
        "ix_activity_events_actor_account_id",
        "activity_events",
        ["actor_account_id"],
        unique=False,
    )
    op.create_index(
        "ix_activity_events_created_at",
        "activity_events",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_activity_events_created_at", table_name="activity_events")
    op.drop_index("ix_activity_events_actor_account_id", table_name="activity_events")
    op.drop_index("ix_activity_events_entity_id", table_name="activity_events")
    op.drop_index("ix_activity_events_entity_type", table_name="activity_events")
    op.drop_table("activity_events")

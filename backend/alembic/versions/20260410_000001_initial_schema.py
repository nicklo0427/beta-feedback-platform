"""Initial schema baseline."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260410_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("locale", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("password_hash", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_accounts_email", "accounts", ["email"], unique=True)

    op.create_table(
        "actor_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("account_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("expires_at", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_actor_sessions_account_id",
        "actor_sessions",
        ["account_id"],
        unique=False,
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_account_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_projects_owner_account_id",
        "projects",
        ["owner_account_id"],
        unique=False,
    )

    op.create_table(
        "campaigns",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_platforms", sa.JSON(), nullable=False),
        sa.Column("version_label", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_campaigns_project_id", "campaigns", ["project_id"], unique=False)
    op.create_index("ix_campaigns_status", "campaigns", ["status"], unique=False)

    op.create_table(
        "campaign_safety",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("campaign_id", sa.String(), nullable=False),
        sa.Column("distribution_channel", sa.String(), nullable=False),
        sa.Column("source_label", sa.String(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("risk_level", sa.String(), nullable=False),
        sa.Column("review_status", sa.String(), nullable=False),
        sa.Column("official_channel_only", sa.Boolean(), nullable=False),
        sa.Column("risk_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_campaign_safety_campaign_id",
        "campaign_safety",
        ["campaign_id"],
        unique=True,
    )

    op.create_table(
        "eligibility_rules",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("campaign_id", sa.String(), nullable=False),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("os_name", sa.String(), nullable=True),
        sa.Column("os_version_min", sa.String(), nullable=True),
        sa.Column("os_version_max", sa.String(), nullable=True),
        sa.Column("install_channel", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_eligibility_rules_campaign_id",
        "eligibility_rules",
        ["campaign_id"],
        unique=False,
    )

    op.create_table(
        "device_profiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("device_model", sa.String(), nullable=False),
        sa.Column("os_name", sa.String(), nullable=False),
        sa.Column("install_channel", sa.String(), nullable=True),
        sa.Column("os_version", sa.String(), nullable=True),
        sa.Column("browser_name", sa.String(), nullable=True),
        sa.Column("browser_version", sa.String(), nullable=True),
        sa.Column("locale", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("owner_account_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_device_profiles_platform",
        "device_profiles",
        ["platform"],
        unique=False,
    )
    op.create_index(
        "ix_device_profiles_owner_account_id",
        "device_profiles",
        ["owner_account_id"],
        unique=False,
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("campaign_id", sa.String(), nullable=False),
        sa.Column("device_profile_id", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("instruction_summary", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("submitted_at", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tasks_campaign_id", "tasks", ["campaign_id"], unique=False)
    op.create_index(
        "ix_tasks_device_profile_id",
        "tasks",
        ["device_profile_id"],
        unique=False,
    )
    op.create_index("ix_tasks_status", "tasks", ["status"], unique=False)

    op.create_table(
        "feedback",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("task_id", sa.String(), nullable=False),
        sa.Column("campaign_id", sa.String(), nullable=False),
        sa.Column("device_profile_id", sa.String(), nullable=True),
        sa.Column("summary", sa.String(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("reproduction_steps", sa.Text(), nullable=True),
        sa.Column("expected_result", sa.Text(), nullable=True),
        sa.Column("actual_result", sa.Text(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(), nullable=False),
        sa.Column("developer_note", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.String(), nullable=False),
        sa.Column("resubmitted_at", sa.String(), nullable=True),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feedback_task_id", "feedback", ["task_id"], unique=False)
    op.create_index("ix_feedback_campaign_id", "feedback", ["campaign_id"], unique=False)
    op.create_index(
        "ix_feedback_device_profile_id",
        "feedback",
        ["device_profile_id"],
        unique=False,
    )
    op.create_index(
        "ix_feedback_review_status",
        "feedback",
        ["review_status"],
        unique=False,
    )

    op.create_table(
        "participation_requests",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("campaign_id", sa.String(), nullable=False),
        sa.Column("tester_account_id", sa.String(), nullable=False),
        sa.Column("device_profile_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("decision_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("updated_at", sa.String(), nullable=False),
        sa.Column("decided_at", sa.String(), nullable=True),
        sa.Column("linked_task_id", sa.String(), nullable=True),
        sa.Column("assignment_created_at", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_participation_requests_campaign_id",
        "participation_requests",
        ["campaign_id"],
        unique=False,
    )
    op.create_index(
        "ix_participation_requests_tester_account_id",
        "participation_requests",
        ["tester_account_id"],
        unique=False,
    )
    op.create_index(
        "ix_participation_requests_device_profile_id",
        "participation_requests",
        ["device_profile_id"],
        unique=False,
    )
    op.create_index(
        "ix_participation_requests_status",
        "participation_requests",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_participation_requests_linked_task_id",
        "participation_requests",
        ["linked_task_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_participation_requests_linked_task_id", table_name="participation_requests")
    op.drop_index("ix_participation_requests_status", table_name="participation_requests")
    op.drop_index(
        "ix_participation_requests_device_profile_id",
        table_name="participation_requests",
    )
    op.drop_index(
        "ix_participation_requests_tester_account_id",
        table_name="participation_requests",
    )
    op.drop_index("ix_participation_requests_campaign_id", table_name="participation_requests")
    op.drop_table("participation_requests")

    op.drop_index("ix_feedback_review_status", table_name="feedback")
    op.drop_index("ix_feedback_device_profile_id", table_name="feedback")
    op.drop_index("ix_feedback_campaign_id", table_name="feedback")
    op.drop_index("ix_feedback_task_id", table_name="feedback")
    op.drop_table("feedback")

    op.drop_index("ix_tasks_status", table_name="tasks")
    op.drop_index("ix_tasks_device_profile_id", table_name="tasks")
    op.drop_index("ix_tasks_campaign_id", table_name="tasks")
    op.drop_table("tasks")

    op.drop_index("ix_device_profiles_owner_account_id", table_name="device_profiles")
    op.drop_index("ix_device_profiles_platform", table_name="device_profiles")
    op.drop_table("device_profiles")

    op.drop_index("ix_eligibility_rules_campaign_id", table_name="eligibility_rules")
    op.drop_table("eligibility_rules")

    op.drop_index("ix_campaign_safety_campaign_id", table_name="campaign_safety")
    op.drop_table("campaign_safety")

    op.drop_index("ix_campaigns_status", table_name="campaigns")
    op.drop_index("ix_campaigns_project_id", table_name="campaigns")
    op.drop_table("campaigns")

    op.drop_index("ix_projects_owner_account_id", table_name="projects")
    op.drop_table("projects")

    op.drop_index("ix_actor_sessions_account_id", table_name="actor_sessions")
    op.drop_table("actor_sessions")

    op.drop_index("ix_accounts_email", table_name="accounts")
    op.drop_table("accounts")

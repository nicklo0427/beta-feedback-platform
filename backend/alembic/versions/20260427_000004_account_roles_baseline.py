"""Add account roles baseline."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260427_000004"
down_revision = "20260412_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("accounts") as batch_op:
        batch_op.add_column(sa.Column("roles", sa.JSON(), nullable=True))

    accounts = sa.table(
        "accounts",
        sa.column("id", sa.String()),
        sa.column("role", sa.String()),
        sa.column("roles", sa.JSON()),
    )
    connection = op.get_bind()
    existing_accounts = connection.execute(
        sa.select(accounts.c.id, accounts.c.role)
    ).mappings().all()

    for account in existing_accounts:
        connection.execute(
            accounts.update()
            .where(accounts.c.id == account["id"])
            .values(roles=[account["role"]])
        )

    with op.batch_alter_table("accounts") as batch_op:
        batch_op.alter_column("roles", existing_type=sa.JSON(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("accounts") as batch_op:
        batch_op.drop_column("roles")

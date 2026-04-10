"""add sales cancel audit fields

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f7
Create Date: 2026-04-10 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b7c8d9e0f1a2"
down_revision: str | None = "a1b2c3d4e5f7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "sales",
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "sales",
        sa.Column("cancelled_by_user_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_sales_cancelled_by_user_id_users"),
        "sales",
        "users",
        ["cancelled_by_user_id"],
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_sales_cancelled_by_user_id_users"),
        "sales",
        type_="foreignkey",
    )
    op.drop_column("sales", "cancelled_by_user_id")
    op.drop_column("sales", "cancelled_at")

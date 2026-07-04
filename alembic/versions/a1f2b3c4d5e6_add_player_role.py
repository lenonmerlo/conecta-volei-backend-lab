"""add player role

Revision ID: a1f2b3c4d5e6
Revises: d545fcee814f
Create Date: 2026-07-04 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a1f2b3c4d5e6"
down_revision: str | None = "d545fcee814f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "players",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="player",
        ),
    )
    op.alter_column("players", "role", server_default=None)


def downgrade() -> None:
    op.drop_column("players", "role")
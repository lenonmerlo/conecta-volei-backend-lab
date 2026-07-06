"""create audit logs table

Revision ID: b2c3d4e5f6a7
Revises: a1f2b3c4d5e6
Create Date: 2026-07-06 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "a1f2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("actor_player_id", sa.String(length=36), nullable=True),
        sa.Column("target_player_id", sa.String(length=36), nullable=True),
        sa.Column("game_id", sa.String(length=40), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_player_id"],
            ["players.id"],
            name=op.f("fk_audit_logs_actor_player_id_players"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["target_player_id"],
            ["players.id"],
            name=op.f("fk_audit_logs_target_player_id_players"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["game_id"],
            ["games.id"],
            name=op.f("fk_audit_logs_game_id_games"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
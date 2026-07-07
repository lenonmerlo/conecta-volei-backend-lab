"""create game teams table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-06 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: str | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "game_teams",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("game_id", sa.String(length=50), nullable=False),
        sa.Column("team_name", sa.String(length=20), nullable=False),
        sa.Column("players", sa.JSON(), nullable=False),
        sa.Column("total_level", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["game_id"],
            ["games.id"],
            name="fk_game_teams_game_id_games",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_game_teams"),
    )
    op.create_index(
        "ix_game_teams_game_id",
        "game_teams",
        ["game_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_game_teams_game_id", table_name="game_teams")
    op.drop_table("game_teams")
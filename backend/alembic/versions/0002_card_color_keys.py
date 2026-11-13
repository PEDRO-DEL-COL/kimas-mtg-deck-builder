"""add denormalised color keys and cmc index to cards

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-13 18:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("cards", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("colors_key", sa.String(length=5), nullable=False, server_default="")
        )
        batch_op.add_column(
            sa.Column("color_identity_key", sa.String(length=5), nullable=False, server_default="")
        )
        batch_op.create_index("ix_cards_cmc", ["cmc"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("cards", schema=None) as batch_op:
        batch_op.drop_index("ix_cards_cmc")
        batch_op.drop_column("color_identity_key")
        batch_op.drop_column("colors_key")

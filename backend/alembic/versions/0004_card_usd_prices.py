"""add Scryfall USD price columns to cards

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-13 20:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("cards", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("price_usd", sa.Numeric(precision=10, scale=2), nullable=True)
        )
        batch_op.add_column(
            sa.Column("price_usd_foil", sa.Numeric(precision=10, scale=2), nullable=True)
        )
        batch_op.add_column(
            sa.Column("price_usd_etched", sa.Numeric(precision=10, scale=2), nullable=True)
        )
        batch_op.add_column(
            sa.Column("prices_updated_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.create_index("ix_cards_price_usd", ["price_usd"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("cards", schema=None) as batch_op:
        batch_op.drop_index("ix_cards_price_usd")
        batch_op.drop_column("prices_updated_at")
        batch_op.drop_column("price_usd_etched")
        batch_op.drop_column("price_usd_foil")
        batch_op.drop_column("price_usd")

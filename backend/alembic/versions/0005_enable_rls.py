"""enable row level security on all tables (PostgreSQL only)

No policies are created: anon/authenticated roles going through PostgREST are
denied by default. The FastAPI backend connects directly as the table owner,
which bypasses RLS.

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-13 20:00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLES = (
    "users",
    "cards",
    "card_prices",
    "price_runs",
    "decks",
    "deck_cards",
    "alembic_version",
)


def upgrade() -> None:
    if op.get_context().dialect.name != "postgresql":
        return
    for table in _TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    if op.get_context().dialect.name != "postgresql":
        return
    for table in _TABLES:
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
